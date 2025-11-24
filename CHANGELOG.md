# Changelog

All notable changes to PDF Tools API will be documented in this file.

## [0.1.1] - 2025-11-23

### Fixed
- **CRITICAL**: `compress_pdf()` now actually uses `dpi`, `image_quality`, and `color_mode` parameters
  - Previously ignored all parameters and only did basic compression
  - Now renders pages as images at specified DPI and re-encodes with quality settings
  - Note: This converts pages to images, which may affect text selectability
- **CRITICAL**: CORS configuration properly handles wildcard ("*") origins
  - Fixed `CORS_ORIGINS="*"` being split incorrectly
  - Disables credentials when using wildcard to prevent startup crash
  - Added `cors_origins_list` property for proper handling

### Fixed - Error Handling
- Fixed memory leak in image-to-PDF conversion
  - Temp RGB files now properly cleaned up on all error paths
  - Added error cleanup in all exception handlers
- Fixed unsafe transparency handling in image conversion
  - Safer alpha channel extraction with fallback
  - Prevents crashes on edge-case image modes
- Improved health check endpoint
  - Now validates temp directory exists and is writable
  - Returns "degraded" status if temp dir unavailable
  - Includes temp dir path and writability status

### Added - Optimizations
- Migrated to Pydantic Settings for configuration
  - Type-safe configuration validation
  - Better environment variable handling
  - Added helper properties (`max_file_size_bytes`, `cors_origins_list`)
- Added cache control headers to all file responses
  - Prevents browser caching of dynamically generated PDFs
  - Headers: `Cache-Control: no-cache, no-store, must-revalidate`
- Added compression metrics logging
  - Logs original size, compressed size, and compression ratio
  - Helps monitor compression effectiveness

### Changed
- Updated `requirements.txt`
  - Added `pydantic-settings==2.1.0`
  - Removed duplicate dependencies
  - Cleaned up requirements list
- Updated all documentation
  - README.md with new features and fixes
  - AZURE_APP_SERVICE.md deployment guide
  - AZURE_CONTAINER_INSTANCES.md deployment guide
  - AZURE_DEPLOYMENT.md comprehensive guide
- Improved error messages for file size violations
- Better structured error handling throughout

## [0.1.0] - Initial Release

### Added
- Image to PDF conversion endpoint
- PDF merging endpoint
- PDF compression endpoint
- Docker support
- Azure deployment configuration
- Health check endpoint
- CORS support
- Async file processing
- Automatic temp file cleanup
