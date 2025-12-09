"""
DEVORA Mobile Export Routes - Export to React Native & Expo
@version 1.0.0

Features:
- Export web projects to Expo
- Convert React components to React Native
- Generate complete mobile app structure
- Download as ZIP
- Support for Expo Router
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse, Response
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import io
import uuid
import json
import logging
from datetime import datetime, timezone

from services.mobile_export_service import (
    mobile_export_service,
    SourceFile,
    ExportResult,
    MobileFramework
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/mobile", tags=["mobile-export"])


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class FileInput(BaseModel):
    """Input file from web project"""
    name: str
    content: str
    type: Optional[str] = "unknown"  # component, page, style, util


class MobileExportRequest(BaseModel):
    """Request for mobile export"""
    project_id: Optional[str] = None
    project_name: str
    files: List[FileInput]
    framework: str = "expo"  # expo, expo-router, react-native-cli
    use_typescript: bool = True
    include_navigation: bool = True


class ExportProgressResponse(BaseModel):
    """Export progress response"""
    id: str
    status: str
    progress: int
    message: str
    current_file: Optional[str] = None


class ExportResultResponse(BaseModel):
    """Export result response"""
    id: str
    success: bool
    download_url: Optional[str] = None
    error: Optional[str] = None
    stats: Dict[str, int] = {}
    warnings: List[str] = []
    files_count: int = 0
    created_at: str


class ConvertedFileInfo(BaseModel):
    """Info about a converted file"""
    path: str
    original: Optional[str] = None
    size: int


class ExportPreviewResponse(BaseModel):
    """Preview of export result"""
    files: List[ConvertedFileInfo]
    total_size: int
    framework: str
    warnings: List[str]


# In-memory storage for exports
exports_store: Dict[str, Dict] = {}


# =============================================================================
# EXPORT ENDPOINTS
# =============================================================================

@router.post("/export", response_model=ExportResultResponse)
async def export_to_mobile(request: MobileExportRequest):
    """
    Export web project to mobile (React Native/Expo)

    - Converts React components to React Native
    - Generates complete Expo project structure
    - Returns download link for ZIP file
    """
    export_id = str(uuid.uuid4())

    try:
        # Convert input files
        source_files = [
            SourceFile(
                name=f.name,
                content=f.content,
                type=f.type or "unknown"
            )
            for f in request.files
        ]

        # Determine if using Expo Router
        use_expo_router = request.framework == "expo-router" or request.include_navigation

        # Perform export
        result = await mobile_export_service.export_to_expo(
            files=source_files,
            project_name=request.project_name,
            use_expo_router=use_expo_router
        )

        if not result.success:
            return ExportResultResponse(
                id=export_id,
                success=False,
                error=result.error,
                stats={},
                warnings=[],
                files_count=0,
                created_at=datetime.now(timezone.utc).isoformat()
            )

        # Store export for download
        exports_store[export_id] = {
            "id": export_id,
            "project_name": request.project_name,
            "zip_content": result.zip_content,
            "files": result.files,
            "stats": result.stats,
            "warnings": result.warnings,
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        return ExportResultResponse(
            id=export_id,
            success=True,
            download_url=f"/api/mobile/download/{export_id}",
            stats=result.stats,
            warnings=result.warnings,
            files_count=len(result.files),
            created_at=datetime.now(timezone.utc).isoformat()
        )

    except Exception as e:
        logger.exception(f"[MobileExport] Error: {e}")
        return ExportResultResponse(
            id=export_id,
            success=False,
            error=str(e),
            stats={},
            warnings=[],
            files_count=0,
            created_at=datetime.now(timezone.utc).isoformat()
        )


@router.post("/preview", response_model=ExportPreviewResponse)
async def preview_export(request: MobileExportRequest):
    """
    Preview mobile export without generating ZIP

    Returns list of files that would be generated
    """
    try:
        source_files = [
            SourceFile(
                name=f.name,
                content=f.content,
                type=f.type or "unknown"
            )
            for f in request.files
        ]

        use_expo_router = request.framework == "expo-router" or request.include_navigation

        result = await mobile_export_service.export_to_expo(
            files=source_files,
            project_name=request.project_name,
            use_expo_router=use_expo_router
        )

        if not result.success:
            raise HTTPException(status_code=400, detail=result.error)

        files_info = [
            ConvertedFileInfo(
                path=f.path,
                original=f.original,
                size=len(f.content.encode('utf-8'))
            )
            for f in result.files
        ]

        total_size = sum(f.size for f in files_info)

        return ExportPreviewResponse(
            files=files_info,
            total_size=total_size,
            framework=request.framework,
            warnings=result.warnings
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"[MobileExport] Preview error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/{export_id}")
async def download_export(export_id: str):
    """
    Download exported mobile project as ZIP
    """
    if export_id not in exports_store:
        raise HTTPException(status_code=404, detail="Export not found")

    export_data = exports_store[export_id]
    zip_content = export_data.get("zip_content")

    if not zip_content:
        raise HTTPException(status_code=404, detail="ZIP file not available")

    project_name = export_data.get("project_name", "mobile-app")
    filename = f"{project_name.lower().replace(' ', '-')}-mobile.zip"

    return Response(
        content=zip_content,
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )


@router.get("/file/{export_id}/{file_path:path}")
async def get_exported_file(export_id: str, file_path: str):
    """
    Get a specific file from the export
    """
    if export_id not in exports_store:
        raise HTTPException(status_code=404, detail="Export not found")

    export_data = exports_store[export_id]
    files = export_data.get("files", [])

    for f in files:
        if f.path == file_path:
            return Response(
                content=f.content,
                media_type="text/plain",
                headers={
                    "Content-Type": "text/plain; charset=utf-8"
                }
            )

    raise HTTPException(status_code=404, detail="File not found")


@router.get("/status/{export_id}", response_model=ExportResultResponse)
async def get_export_status(export_id: str):
    """Get export status by ID"""
    if export_id not in exports_store:
        raise HTTPException(status_code=404, detail="Export not found")

    export_data = exports_store[export_id]

    return ExportResultResponse(
        id=export_id,
        success=True,
        download_url=f"/api/mobile/download/{export_id}",
        stats=export_data.get("stats", {}),
        warnings=export_data.get("warnings", []),
        files_count=len(export_data.get("files", [])),
        created_at=export_data.get("created_at", "")
    )


# =============================================================================
# CONVERSION UTILITIES
# =============================================================================

class ConvertComponentRequest(BaseModel):
    """Request to convert a single component"""
    content: str
    filename: str


class ConvertComponentResponse(BaseModel):
    """Response from component conversion"""
    success: bool
    converted: str
    warnings: List[str]


@router.post("/convert/component", response_model=ConvertComponentResponse)
async def convert_single_component(request: ConvertComponentRequest):
    """
    Convert a single React component to React Native

    Useful for testing conversions
    """
    try:
        from services.mobile_export_service import ReactToReactNativeConverter

        converter = ReactToReactNativeConverter()
        converted, warnings = converter.convert_component(
            request.content,
            request.filename
        )

        return ConvertComponentResponse(
            success=True,
            converted=converted,
            warnings=warnings
        )

    except Exception as e:
        logger.exception(f"[MobileExport] Conversion error: {e}")
        return ConvertComponentResponse(
            success=False,
            converted="",
            warnings=[str(e)]
        )


class ConvertStylesRequest(BaseModel):
    """Request to convert Tailwind classes"""
    classes: str


class ConvertStylesResponse(BaseModel):
    """Response from style conversion"""
    styles: Dict[str, Any]


@router.post("/convert/styles", response_model=ConvertStylesResponse)
async def convert_tailwind_to_stylesheet(request: ConvertStylesRequest):
    """
    Convert Tailwind CSS classes to React Native StyleSheet

    Example:
    - Input: "flex items-center justify-between p-4 bg-white rounded-lg"
    - Output: StyleSheet-compatible object
    """
    try:
        from services.mobile_export_service import CSSToStyleSheetConverter

        styles = CSSToStyleSheetConverter.convert_tailwind_classes(request.classes)

        return ConvertStylesResponse(styles=styles)

    except Exception as e:
        logger.exception(f"[MobileExport] Style conversion error: {e}")
        return ConvertStylesResponse(styles={})


# =============================================================================
# FRAMEWORK INFO
# =============================================================================

class FrameworkInfo(BaseModel):
    """Mobile framework information"""
    id: str
    name: str
    description: str
    features: List[str]
    recommended: bool


@router.get("/frameworks", response_model=List[FrameworkInfo])
async def list_frameworks():
    """List available mobile frameworks"""
    return [
        FrameworkInfo(
            id="expo-router",
            name="Expo Router",
            description="File-based routing for Expo, similar to Next.js",
            features=[
                "File-based routing",
                "Deep linking",
                "TypeScript support",
                "Native navigation",
                "Tab navigation built-in"
            ],
            recommended=True
        ),
        FrameworkInfo(
            id="expo",
            name="Expo (Traditional)",
            description="Standard Expo with React Navigation",
            features=[
                "React Navigation",
                "Manual route config",
                "Full flexibility",
                "Easy to customize"
            ],
            recommended=False
        ),
        FrameworkInfo(
            id="react-native-cli",
            name="React Native CLI",
            description="Bare React Native without Expo",
            features=[
                "Full native access",
                "Custom native modules",
                "Smaller bundle size",
                "More setup required"
            ],
            recommended=False
        )
    ]


# =============================================================================
# EXPORT HISTORY
# =============================================================================

class ExportHistoryItem(BaseModel):
    """Export history item"""
    id: str
    project_name: str
    files_count: int
    created_at: str


@router.get("/history", response_model=List[ExportHistoryItem])
async def get_export_history(limit: int = 20):
    """Get recent export history"""
    exports = list(exports_store.values())
    exports.sort(key=lambda e: e.get("created_at", ""), reverse=True)

    return [
        ExportHistoryItem(
            id=e["id"],
            project_name=e.get("project_name", "Unknown"),
            files_count=len(e.get("files", [])),
            created_at=e.get("created_at", "")
        )
        for e in exports[:limit]
    ]


@router.delete("/{export_id}")
async def delete_export(export_id: str):
    """Delete an export"""
    if export_id not in exports_store:
        raise HTTPException(status_code=404, detail="Export not found")

    del exports_store[export_id]

    return {"success": True, "message": "Export deleted"}
