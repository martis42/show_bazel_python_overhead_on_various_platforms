load("@rules_python//python:defs.bzl", "py_test")

[
    py_test(
        name = "some_test_{}".format(x),
        srcs = ["some_test.py"],
        main = "some_test.py",
    )
    for x in range(0, 100)
]
