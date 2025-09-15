# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Build Commands
- **Build project**: `hvigorw assembleHap` - Builds the entire OpenHarmony application
- **Clean build**: `hvigorw clean` followed by `hvigorw assembleHap` - Clean build process
- **Build debug version**: `hvigorw assembleHap --mode debug` - Build debug variant
- **Build release version**: `hvigorw assembleHap --mode release` - Build release variant

### Lint and Code Quality
- **Lint code**: Code linting is configured via `code-linter.json5` which includes security and performance rules
- **Lint files**: All `.ets` files are linted with TypeScript ESLint and performance/security rules
- **Ignore patterns**: Tests, mocks, build artifacts, and node_modules are excluded from linting

### Testing
- **Unit tests**: Run `hvigorw test` to execute unit tests across all modules
- **Local unit tests**: Located in `src/test/` directories (LocalUnit.test.ets, List.test.ets)
- **OpenHarmony tests**: Located in `src/ohosTest/` directories (Ability.test.ets, List.test.ets)
- **Test framework**: Uses `@ohos/hypium` and `@ohos/hamock` for testing

## Project Architecture

### Module Structure
This is an OpenHarmony application using a modular HSP (Harmony Shared Package) architecture:

1. **Entry Module** (`product/default/`): Main application entry point with lifecycle management
2. **Common HSP** (`commons/common/`): Shared base functionality including HTTP clients, databases, logging
3. **Feature HSP** (`features/feature/`): Business logic and UI components for news functionality

### Technology Stack
- **Language**: ArkTS (TypeScript-like language for OpenHarmony)
- **Build System**: Hvigor build system with Node.js toolchain
- **HTTP Client**: `@ohos/axios` for network requests
- **Markdown Rendering**: `@lidary/markdown` for content display
- **Data Storage**: KV database and Preferences for local data persistence

### Key Components Architecture

#### NewsManager (`features/feature/src/main/ets/managers/NewsManager.ets`)
Central data management class that handles:
- Server health checking before API calls
- News article list fetching and caching to KV database
- News swiper/banner image data management
- Local data persistence and retrieval

#### Network Layer
- **Base URL Configuration**: Server address configured in `commons/common/src/main/ets/modules/constants.ets:38`
- **HTTP Client**: Wrapped Axios implementation in `commons/common/src/main/ets/api/http/AxiosHttp.ets`
- **API Services**: Separate API classes for news, server health, and swiper data

#### Data Storage Strategy
- **KV Database**: For caching news articles and swiper data using `APP_KV_DB` store
- **Preferences**: For user configuration like theme mode and font size
- **Database Keys**: Defined in `KV_DB_KEYS` enum for consistent data access

#### Responsive Design System
- **Breakpoint System**: Multi-device adaptation using breakpoint-based responsive design
- **Device Support**: Phone, tablet, and foldable device layouts
- **Theme Support**: Light/dark mode with system following capability

### Key Configuration Files
- `build-profile.json5`: Defines app signing, modules, and build targets
- `oh-package.json5`: Dependencies and package configuration
- `code-linter.json5`: ESLint rules including security and performance checks
- `hvigorfile.ts`: Build task configuration using Hvigor plugins

### Development Workflow
1. Use NewsManager for all data operations instead of direct API calls
2. Always check server health before making network requests
3. Implement proper error handling with BusinessError type casting
4. Use the logger utility for consistent logging across modules
5. Follow the modular HSP architecture - common utilities in Common HSP, business features in Feature HSP
6. Use the breakpoint system for responsive UI development

### Data Flow Pattern
```
UI Component → Manager Class → API Service → HTTP Client → Server
                     ↓
              KV Database Cache
```

All data should flow through manager classes that handle caching, error handling, and server health checks.