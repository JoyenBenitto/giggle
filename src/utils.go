package main

import (
    "fmt"
    "os"
)

func check(e error) {
    if e != nil {
        panic(e)
    }
}

func reader() {

    dat, err := os.ReadFile("../test_src/index.md")
    check(err)
    fmt.Print(string(dat))
}