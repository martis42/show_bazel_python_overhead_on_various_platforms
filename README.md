# show_bazel_python_overhead_on_various_platforms

CI Trigger

Host toolchain

| Setup                                    | Time first run | Time second run |
|------------------------------------------|----------------|-----------------|
| normal - ubuntu-22.04                    | 9 s            | 3 s             |
| normal - macos-12                        | 78 s           | 6 s             |
| normal - windows-2022                    | 70 s           | 5 s             |
| `--nolegacy_runfiles` - ubuntu-22.04     | 8 s            | 3 s             |
| `--nolegacy_runfiles` - macos-12         | 63 s           | 5 s             |
| `--nolegacy_runfiles` - windows-2022     | 78 s           | 5 s             |
| `--spawn_strategy=local` - ubuntu-22.04  | 8 s            | 3 s             |
| `--spawn_strategy=local` - macos-12      | 62 s           | 4 s             |
| `--spawn_strategy=local` - windows-2022  | 67 s           | 5 s             |


Hermetic rules_python toolchain

| Setup                                                        | Time first run | Time second run |
|--------------------------------------------------------------|----------------|-----------------|
| normal - ubuntu-22.04                                        | 25 s           | 9 s             |
| normal - macos-12                                            | 115 s          | 27 s            |
| normal - windows-2022                                        | 265 s          | 169 s           |
| `--nolegacy_runfiles` - ubuntu-22.04                         | 18 s           | 5 s             |
| `--nolegacy_runfiles` - macos-12                             | 87 s           | 16 s            |
| `--nolegacy_runfiles` - windows-2022                         | 277 s          | 173 s           |
| `--spawn_strategy=local` - ubuntu-22.04                      |                |                 |
| `--spawn_strategy=local` - macos-12                          |                |                 |
| `--spawn_strategy=local` - windows-2022                      | 226 s          | 171 s           |
| `--spawn_strategy=local --nolegacy_runfiles` - ubuntu-22.04  | 14 s           | 4 s             |
| `--spawn_strategy=local --nolegacy_runfiles` - macos-12      | 119 s          | 8 s             |
| `--spawn_strategy=local --nolegacy_runfiles` - windows-2022  | 265 s          | 173 s           |
