package main

import (
    "flag"
    "fmt"
    "os"
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
    
    os.MkdirAll(*build_dir, os.ModePerm)
    //index.html generator
    index_html_generator( "test_src/index.md",*build_dir)
    
}
