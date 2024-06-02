// The following folder consists of utility functions

/*
Functions in the file:
* reader: reads and outputs file content as string
* yaml_reader: reads YAML and outputs a yaml struct
*/

package main

import (
    "os"
    "fmt"
    "io/ioutil"
    "gopkg.in/yaml.v2"
)

func check(e error) {
    if e != nil {
        panic(e)
    }
}

func reader(path string) []byte{
    dat, err := os.ReadFile(path)
    check(err)
    return dat
}

func dump(path string, str string){
    file, err := os.Create(path)
    if(err != nil){
        panic(err)
    }
    defer file.Close()
    _, err = file.WriteString(str)
    if(err != nil){
        panic(err)
    }
}

func yaml_reader(file_path string) map[string]interface{}{
    /*
    The yaml reader
    */
    obj := make(map[string]interface{})
    yamlFile, err := ioutil.ReadFile(file_path)

    if err != nil {
     fmt.Printf("yamlFile.Get err #%v ", err)
    }

    err = yaml.Unmarshal(yamlFile, obj)
    if err != nil {
     fmt.Printf("Unmarshal: %v", err)
    }
    return obj
}