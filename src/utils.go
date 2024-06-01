// The following folder consists of utility functions

/*
Functions in the file:
* reader: reads and outputs file content as string
* yaml_reader: reads YAML and outputs a yaml struct
*/

package main

import (
    "os"
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