package main

import (
    "flag"
    "fmt"
)

func main() {
    /*
    Top-level for the giggle static site generator
    */

    config_yaml := flag.String("config_yaml", 
                                "./default_config.yaml", 
                                "Path to the config yaml")

    theme_yaml := flag.String("theme_yaml", 
                                "./default_config.yaml", 
                                "Path to the yaml")

    build_dir := flag.String("build_dir", 
                             "./build", 
                             "Path to the build directory")

    flag.Parse()

    fmt.Println("build_dir:", *build_dir)
    fmt.Println("config:", *config_yaml)
    fmt.Println("config:", *theme_yaml)

    // Reads the input file
    val := reader("../test_src/index.md")
    fmt.Printf("%s",string(val))

    //Markdown rendered
    html := mdToHTML(val)
    fmt.Println(string(html))

    dump("../index.html", string(html))
}
