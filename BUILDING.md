# Building REST in Pawn

The extension does not depend on Metamod or a game-specific HL2SDK. The same
build supports the games supported by the corresponding SourceMod runtime;
choose the operating system and architecture of the server process.

## SourceMod SDK compatibility

| SourceMod | SDK branch | Architectures in CI | Release archive marker |
| --- | --- | --- | --- |
| 1.7 | `1.7-dev` | x86 | `sm1.7` |
| 1.8 | `1.8-dev` | x86 | `sm1.8` |
| 1.9 | `1.9-dev` | x86 | `sm1.9` |
| 1.10 | `1.10-dev` | x86 | `sm1.10` |
| 1.11 | `1.11-dev` | x86, x86_64 | `sm1.11` |
| 1.12 | `1.12-dev` | x86, x86_64 | no marker (original archive names) |
| 1.13 | `master` | x86, x86_64 | `sm1.13` |

Choose the archive matching the server's SourceMod version and operating
system. SourceMod versions before 1.7 are not covered by this build matrix.

Build these variants separately: SourceMod 1.13 changes the SourcePawn and
forward binary interfaces. Successful compilation against both SDKs does not
make a binary compiled with one SDK interchangeable with the other.

CI builds every SDK variant on Linux and Windows, using the architectures in
the table. HTTP and JSON natives and the Pawn includes are shared between the
variants. Compile plugins using the compiler/includes for the oldest SourceMod
version they need to run on; an extension build does not make newer plugin
bytecode compatible with an older SourcePawn runtime.

For SourcePawn 1.7, HTTP callbacks must be declared `public` (including
callbacks passed to `HTTPRequest` and `HTTPClient`). The bundled test plugin
uses compatible declarations, and the Linux SM 1.7 CI job compiles it with the
official SourcePawn 1.7.3 compiler. For example:

```sourcepawn
public void OnResponse(HTTPResponse response, any value, const char[] error)
{
    PrintToServer("HTTP status: %d, error: %s", response.Status, error);
}
```

## Local build

Install AMBuild 2.2 or newer and a C/C++ compiler. Linux builds targeting x86
also need the compiler's multilib development packages. Check out SourceMod
with its submodules, selecting the branch from the table. From the extension
source directory (use `--targets=x86` for SM 1.7–1.10):

```sh
mkdir build
cd build
perl ../curl/lib/mk-ca-bundle.pl
python ../configure.py --sm-path=/path/to/sourcemod --enable-optimize --targets=x86,x86_64
ambuild
```

The installable files are in `build/package`. The x86 extension is placed in
`addons/sourcemod/extensions`, and the x64 extension in its `x64` subdirectory.
Use a separate build directory for each SDK. `--sm-path` explicitly selects
the SDK; automatic discovery recognizes `SOURCEMOD17` through `SOURCEMOD113`
and directories named `sourcemod-1.7` through `sourcemod-1.13`, preferring the
newest SDK found. Set `--sm-path` when multiple SDKs are installed.
