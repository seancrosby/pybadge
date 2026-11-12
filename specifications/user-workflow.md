# User distribution workflow

## Options

| Consideration | Install `pybadge` as a package | Fork or clone the repository |
| --- | --- | --- |
| Setup effort | A short install command is convenient once packaging and releases are maintained. Programs still need a separate place to be created and stored. | A checkout gives users the library, examples, and documentation together. Git setup is an extra step unless a prepared copy is provided. |
| Offline use | A first install needs a package source or a preloaded wheel. A pinned wheel can be distributed locally, but adds an artifact and installation step. | A clone needs network access initially. A ZIP or prepared checkout can be distributed for offline use; after that, development needs no network. |
| Version updates | Package versions make upgrades and pinning explicit, but different users can end up with different versions. | A known branch or commit can be pinned. Updating a local copy may require resolving edits made in the same files. |
| Local edits | The installed library stays separate from user programs, reducing accidental library edits. Users need a clear place for their own files. | Users can edit examples and keep programs beside the API and setup guide. They can also accidentally alter shared library files or commit generated files. |
| Sharing | Programs need a separate sharing or submission mechanism. The package does not organize user work. | Users can commit and share programs in the same repository or a separate fork. |
| Maintenance | Requires package metadata, releases, a version policy, and support for installation on desktop Python and the badge's MicroPython filesystem. Desktop dependencies and MicroPython limits may complicate a single package. | Requires maintaining a source repository and handling updates to local copies. It keeps source, examples, and setup instructions together and avoids an additional release channel. |

## Recommendation

Use the repository source as the initial distribution format. Users can fork or
clone it when Git access is available, or receive the same source as a ZIP or
prepared local checkout in a restricted or offline environment. Keep personal
programs in `examples/` or a clearly named work directory, separate from
library internals.

This fits the current project: `pybadge.py` is a single user-facing module, the
API is still being implemented, and programs benefit from having examples and
board setup instructions nearby. It also avoids requiring a desktop package
install followed by a separate transfer of a compatible module to MicroPython.

When the API and packaging are stable, publish versioned releases and, if
useful, offer a host-side pip package for simulator use. Treat badge deployment
as a separate step: copy the MicroPython-compatible `pybadge.py` and required
hardware files to the device. Pin a known release or commit when a repeatable
environment is needed. Packaging is an optional distribution path, not a
prerequisite for using or sharing programs.

## Setup notes

- Provide a prepared checkout or ZIP when users cannot rely on network access;
  include the source and examples needed for the intended work.
- Keep user programs under `examples/` or a clearly named work directory.
  Normal use should not require changing library internals.
- Identify a starter commit or release when users need a consistent API.
- Use an existing sharing or submission mechanism; publishing a package is a
  maintainer task, not a prerequisite for using the wrapper.
