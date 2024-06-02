package main

import (
    "github.com/gomarkdown/markdown"
    //"github.com/gomarkdown/markdown/ast"
	 "github.com/gomarkdown/markdown/html"
	 "github.com/gomarkdown/markdown/parser"
	 "fmt"
	 "path/filepath"
)

func mdToHTML(md []byte) []byte {
	/*
	Converts markdown to HTML
	*/
	
	// create markdown parser with extensions
	extensions := parser.CommonExtensions | parser.AutoHeadingIDs | parser.NoEmptyLineBeforeBlock
	p := parser.NewWithExtensions(extensions)
	doc := p.Parse(md)

	// create HTML renderer with extensions
	htmlFlags := html.CommonFlags | html.HrefTargetBlank
	opts := html.RendererOptions{Flags: htmlFlags}
	renderer := html.NewRenderer(opts)

	return markdown.Render(doc, renderer)
}

func index_html_generator(index_markdown_path string, build string, 
						  theme_info map[string]interface{},
						  config_info map[string]interface{}){
	/*
	generates the home page
	*/

	fmt.Println("Generating index.html")
	index_template := reader("constants/index.html")
	rendered_index := index_template
	dump(filepath.Join(build, "index.html"),string(rendered_index))
}