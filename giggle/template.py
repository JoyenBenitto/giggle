blog_template="""
<p> 
  <a href="./blog/{blog_header}.html">
    <h3>{blog_title} - {date} </h3>
  </a>
    {tiny_desc}
</p>
"""

tag_site_template= "\t<li><a href=\"{path_to_page}\">{site_name}</a></li>"

tag_site_head="""
<ul>
{tag_list}
</ul>
"""