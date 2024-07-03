blog_template="""
<li> 
  <a href="./blog/{blog_header}.html"> {blog_title}</a>- <i>{date}</i>
</li>
"""

tag_site_template= "\t<li><a href=\"{path_to_page}\">{site_name}</a></li>"

tag_site_head="""
<ul>
{tag_list}
</ul>
"""