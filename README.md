# stats-generator

_Read this in [Português](README-PT.md)_

A modern, config-driven profile cards generator for GitHub. Create beautiful, auto-updating SVG cards for your README profile.

## Preview

### 🌙 Dark theme

<div align="left">
  <a href="#">
    <img src="cards/overview.svg" alt="Overview Dark" height="165" />
  </a>
  <a href="#">
    <img src="cards/languages.svg" alt="Languages Dark" height="165" />
  </a>
</div>

### 🔆 Light theme

<div align="left">
  <a href="#">
    <img src="cards/overview-light.svg" alt="Overview Light" height="165" />
  </a>
  <a href="#">
    <img src="cards/languages-light.svg" alt="Languages Light" height="165" />
  </a>
</div>

## Features

- **Package-based architecture**: Clean, modular `statsgen` Python package
- **Config-driven**: YAML configuration file + environment variables
- **Jinja2 templating**: Professional template engine for SVG generation
- **Type-safe models**: Dataclass-based data structures
- **CLI support**: Run via `python -m statsgen` with options
- **Matrix workflow**: Parallel theme builds with caching
- **Dark & Light themes**: Automatic theme detection support
- **Official language colors**: Uses GitHub Linguist's color palette

## License

GPL-3.0 License - See [LICENSE](LICENSE) for details.

---

**Note**: Stats are cached by GitHub CDN. Updates may take a few minutes to appear.
