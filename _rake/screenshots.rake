require 'pp'
require 'RMagick'
include Magick

# stolen from https://github.com/cespare/ruby-dedent
class String
  def dedent
    lines = split "\n"
    return self if lines.empty?
    indents = lines.map do |line|
      line =~ /\S/ ? (line.start_with?(" ") ? line.match(/^ +/).offset(0)[1] : 0) : nil
    end
    min_indent = indents.compact.min
    return self if min_indent.zero?
    lines.map { |line| line =~ /\S/ ? line.gsub(/^ {#{min_indent}}/, "") : line }.join "\n"
  end
end

# vars specific to this rake task
CONFIG['gallery_category'] = 'galleries'
CONFIG['screenshots_category'] = 'screenshots'
# where to save the converted images
CONFIG['screenshots_path'] = '/img/screenshots'

# the format of the image files that are written in the screenshots path
CONFIG['image_name'] = '.png'
CONFIG['thumb_size'] = 150
CONFIG['thumb_name'] = '_thumb.gif'
CONFIG['tiny_size'] = 40
CONFIG['tiny_name'] = '_tiny.gif'

# example
# rake screenshots images='../about.gif ../a_nice_image.jpeg ../happiness.tiff' title='My awesome gallery'
# information about screenshot post names is inferred from image names
# thumbnail images are resized versions of the images you specify
# optionally you can create a "_thumb" version of an image, and the image will be generate from that instead
desc "Generate thumbnails, converted full-size images, a gallery page, and screenshot pages"
task :screenshots do
  abort 'no images provided' unless ENV['images']
  images_array = ENV['images'].split(/\s+/).select{ |f| f.any? }

  # ensure all files are readable
  images_array.each{ |image_path|
    abort "not readable: #{image_path}" unless File.readable? image_path
  }

  # from rake task "post"
  abort("rake aborted: '#{CONFIG['posts']}' directory not found.") unless FileTest.directory?(CONFIG['posts'])
  title = ENV["title"]
  slug = title.downcase.strip.gsub(' ', '-').gsub(/[^\w-]/, '')
  begin
    date = (ENV['date'] ? Time.parse(ENV['date']) : Time.now).strftime('%Y-%m-%d')
  rescue Exception => e
    puts "Error - date format must be YYYY-MM-DD, please check you typed it correctly!"
    exit -1
  end

  image_fs_path = File.join(SOURCE, CONFIG['screenshots_path'], date, slug)
  FileUtils.mkpath image_fs_path

  files_to_write = []

  image_names = []
  image_info = []
  images_array.each{ |image_path|
    base_name = File.basename(image_path, ".*")
    image_names << base_name
    dir_name = File.dirname(image_path)

    image_handle = ImageList.new(image_path)
    thumb_handle = ImageList.new(image_path)

    # look for matching customized thumb image
    Dir.glob(File.join(dir_name, "#{base_name}_thumb.*")){ |thumb|
      thumb_handle = ImageList.new(thumb)
    }

    image_path = File.join(image_fs_path, "#{base_name}#{CONFIG['image_name']}")
    files_to_write << image_path
    image_info << { 'handle' => image_handle, 'path' => image_path }

    thumb_path = File.join(image_fs_path, "#{base_name}#{CONFIG['thumb_name']}")
    files_to_write << thumb_path
    image_info << { 'handle' => thumb_handle, 'path' => thumb_path, 'size' => CONFIG['thumb_size'] }

    tiny_path = File.join(image_fs_path, "#{base_name}#{CONFIG['tiny_name']}")
    files_to_write << tiny_path
    image_info << { 'handle' => thumb_handle, 'path' => tiny_path, 'size' => CONFIG['tiny_size'] }
  }

  gallery_file_path = File.join(CONFIG['posts'], CONFIG['gallery_category'])
  FileUtils.mkpath gallery_file_path
  gallery_filename = File.join(gallery_file_path, "#{date}-#{slug}.#{CONFIG['post_ext']}")
  files_to_write << gallery_filename

  screenshot_file_path = File.join(CONFIG['posts'], CONFIG['screenshots_category'])
  FileUtils.mkpath screenshot_file_path
  screenshot_info = []
  image_names.each_with_index{ |image_name, index|
    info = {}
    info['image_name'] = image_name
    info['page_index'] = index + 1
    info['screenshot_filename'] = File.join(screenshot_file_path, "#{date}-#{slug}-screenshot_#{info['page_index']}.#{CONFIG['post_ext']}")
    info['description'] = info['image_name'].gsub('_', ' ')
    screenshot_info << info
    files_to_write << info['screenshot_filename']
  }

  existing_files = []
  files_to_write.each{ |path|
    next unless File.exist? path
    existing_files << path
  }
  if existing_files.any?
    # silly: must manually match spacing here, or dedent gets confused!
    file_list = ["\n"] + existing_files.join("\n").collect{|file| '        '+file}
    ask_text = <<-eos.dedent
      The following file(s) already exist:#{file_list}
      Do you want to overwrite?
    eos
    abort("rake aborted!") if ask(ask_text, ['y', 'n']) == 'n'
  end

  # now write everything out
  image_info.each{ |info|
    puts "Creating image: #{info['path']}"
    if info['size']
      info['handle'].resize_to_fit(info['size']).write(info['path'])
    else
      info['handle'].write(info['path'])
    end
  }
  
  title_tag = title.downcase.strip.gsub(' ', '-').gsub(/[^\w-]/, '')
  puts "Creating gallery: #{gallery_filename}"
  open(gallery_filename, 'w') do |post|
    post.puts <<-eos.dedent
      ---
      layout: post
      title: "#{title}"
      description: ""
      category: #{CONFIG['gallery_category']}
      tags: [#{title_tag}]
      ---
      {% include JB/setup %}
      
      This is a gallery of screenshots for #{title}. Each of the images below is a thumbnail preview. Click on the preview image or description to see the original, full-sized image.
      {% for post in site.posts reversed %}
        {% if post.categories contains '#{CONFIG['screenshots_category']}' %}
          {% if post.tags contains '#{title_tag}' %}
      {% capture img_src %}{{ BASE_PATH }}#{CONFIG['screenshots_path']}/{{ post.date | date: "%Y-%m-%d" }}/{{ post.tags }}/{{ post.slug }}_thumb.gif{% endcapture %}
      
      <h3 id='{{ post.slug }}'><a href='{{ post.url }}'>{{ post.description }}</a></h3>
      
      <p><a href='{{ post.url }}'><img alt='{{ post.description }}' src='{{ img_src }}' /></a></p>
          {% endif %}
        {% endif %}
      {% endfor %}
    eos
  end

  screenshot_info.each{ |info|
    puts "Creating screenshot: #{info['screenshot_filename']}"
    open(info['screenshot_filename'], 'w') do |post|
      post.puts <<-eos.dedent
        ---
        layout: screenshot
        title: "#{title}, screenshot #{info['page_index']}"
        description: "#{info['description'] }"
        category: #{CONFIG['screenshots_category']}
        tags: [#{slug}]
        slug: #{info['image_name']}
        ---
        {% include JB/setup %}
        
        ![#{info['image_name']}]({{ BASE_PATH }}#{CONFIG['screenshots_path']}/#{date}/#{slug}/#{info['image_name']}.png)
      eos
    end
  }
end
