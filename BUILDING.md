# Building REST in Pawn

`sm-1.13` contains the small upstream change for the current SourceMod SDK.
`sm-1.7-plus` adds old SDK support, compatibility CI and release packaging on
top of that change. Each branch adds one commit to its base.

The extension uses SourceMod interfaces without a game-specific HL2SDK.
Choose the package for the server's SourceMod ABI and operating system.

## Release packages

Each release has four ZIP files: two SourceMod ABI groups, each for Linux and
Windows. Every ZIP contains the extension binaries, Pawn includes and CA bundle.

| Archive marker | SourceMod | x86 SDK | x64 SDK |
| --- | --- | --- | --- |
| `sm1.7-1.12` | 1.7-1.12 | `1.7-dev` | `1.10-dev` (for servers on 1.11-1.12) |
| `sm1.13` | 1.13 | `master` | `master` |

The pre-1.13 package uses the oldest compatible SDK for each architecture.
The SourceMod interfaces and SourcePawn virtual methods used by this extension
remain backward compatible through 1.12. The 1.7 native-error check is also
implemented by the newer runtimes. There is no separate download for 1.10,
1.11 or 1.12. Older x86 servers use the same package.

SourceMod 1.13 changes the extension/SourcePawn ABI and needs its own binaries.
The two groups must not be interchanged. x64 is intended for SM 1.11 and newer;
servers on 1.7-1.10 use the x86 binary.

CI compiles against every SDK from 1.7 to 1.13 on Linux and Windows. It also
compiles the test plugin with SourcePawn 1.7.3. The release packager runs on
pushes and pull requests as well as tags, so packaging is checked before
publication. Download `release-packages` from a successful Actions run for the
four installable archives. Tags additionally publish those ZIPs to Releases.
The per-SDK artifacts are compilation checks, not additional release variants.

Compilation and ABI inspection do not replace in-server testing of requests,
callbacks and plugin unloading on the supported games.

## Pawn compatibility

Compile plugins with the compiler/includes for the oldest SourceMod version
on which they need to run. Newer plugin bytecode is not automatically compatible
with older SourcePawn runtimes. SourcePawn 1.7 requires HTTP callbacks to be
`public`, including callbacks passed to `HTTPRequest` and `HTTPClient`:

```sourcepawn
public void OnResponse(HTTPResponse response, any value, const char[] error)
{
    PrintToServer("HTTP status: %d, error: %s", response.Status, error);
}
```

## Local build

Install AMBuild 2.2 or newer and a C/C++ compiler. Linux x86 builds also need
multilib development packages. Check out the desired SourceMod SDK with its
submodules and select it explicitly:

```sh
mkdir build
cd build
perl ../curl/lib/mk-ca-bundle.pl
python ../configure.py --sm-path=/path/to/sourcemod --enable-optimize --targets=x86,x86_64
ambuild
```

Use `--targets=x86` for the 1.7 baseline. Build x64 with the 1.10 SDK for the
pre-1.13 package, and both architectures with `master` for 1.13. Use separate
build directories. Installable files are in `build/package`; x64 binaries are
in `addons/sourcemod/extensions/x64`.

Automatic SDK discovery recognizes `SOURCEMOD17` through `SOURCEMOD113` and
`sourcemod-1.7` through `sourcemod-1.13`, preferring the newest SDK found.
