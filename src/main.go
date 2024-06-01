package main

import (
    "flag"
    "fmt"
)

func main() {

    config_yaml := flag.String("config_yaml", "./default_config.yaml", "Path to the config yaml")
    build_dir := flag.String("build_dir", "./build", "Path to the build directory")

    flag.Parse()

    fmt.Println("build_dir:", *build_dir)
    fmt.Println("config:", *config_yaml)

    //md := []byte(mds)
	 //html := mdToHTML(md)

    reader()
    
    //fmt.Printf("--- Markdown:\n%s\n\n--- HTML:\n%s\n", md, html)
}