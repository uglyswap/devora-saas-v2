"""
DEVORA Mobile Export Service - React Native & Expo Export
@version 1.0.0

Features:
- Convert React web components to React Native
- Generate Expo-compatible project structure
- Support for common UI patterns
- CSS to StyleSheet conversion
- Navigation setup (React Navigation)
- Asset handling
- Platform-specific code generation
"""

import os
import re
import json
import logging
import zipfile
import io
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime, timezone
from enum import Enum
from dataclasses import dataclass, field
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class MobileFramework(str, Enum):
    """Supported mobile frameworks"""
    EXPO = "expo"
    REACT_NATIVE_CLI = "react-native-cli"
    EXPO_ROUTER = "expo-router"


class ExportStatus(str, Enum):
    """Export process status"""
    PENDING = "pending"
    CONVERTING = "converting"
    PACKAGING = "packaging"
    READY = "ready"
    ERROR = "error"


@dataclass
class SourceFile:
    """Source file from web project"""
    name: str
    content: str
    type: str = "unknown"  # component, page, style, util, config


@dataclass
class ConvertedFile:
    """Converted mobile file"""
    path: str
    content: str
    original: Optional[str] = None


@dataclass
class ExportResult:
    """Result of mobile export"""
    success: bool
    files: List[ConvertedFile] = field(default_factory=list)
    zip_content: Optional[bytes] = None
    error: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    stats: Dict[str, int] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class CSSToStyleSheetConverter:
    """Convert CSS/Tailwind to React Native StyleSheet"""

    # CSS property mappings to React Native
    PROPERTY_MAP = {
        # Layout
        "display": "display",
        "flex-direction": "flexDirection",
        "justify-content": "justifyContent",
        "align-items": "alignItems",
        "align-self": "alignSelf",
        "flex-wrap": "flexWrap",
        "flex": "flex",
        "flex-grow": "flexGrow",
        "flex-shrink": "flexShrink",
        "flex-basis": "flexBasis",

        # Dimensions
        "width": "width",
        "height": "height",
        "min-width": "minWidth",
        "max-width": "maxWidth",
        "min-height": "minHeight",
        "max-height": "maxHeight",

        # Spacing
        "margin": "margin",
        "margin-top": "marginTop",
        "margin-right": "marginRight",
        "margin-bottom": "marginBottom",
        "margin-left": "marginLeft",
        "padding": "padding",
        "padding-top": "paddingTop",
        "padding-right": "paddingRight",
        "padding-bottom": "paddingBottom",
        "padding-left": "paddingLeft",

        # Position
        "position": "position",
        "top": "top",
        "right": "right",
        "bottom": "bottom",
        "left": "left",
        "z-index": "zIndex",

        # Typography
        "font-size": "fontSize",
        "font-weight": "fontWeight",
        "font-family": "fontFamily",
        "font-style": "fontStyle",
        "line-height": "lineHeight",
        "letter-spacing": "letterSpacing",
        "text-align": "textAlign",
        "text-decoration": "textDecorationLine",
        "text-transform": "textTransform",
        "color": "color",

        # Background
        "background-color": "backgroundColor",
        "background": "backgroundColor",

        # Border
        "border-width": "borderWidth",
        "border-color": "borderColor",
        "border-style": "borderStyle",
        "border-radius": "borderRadius",
        "border-top-width": "borderTopWidth",
        "border-right-width": "borderRightWidth",
        "border-bottom-width": "borderBottomWidth",
        "border-left-width": "borderLeftWidth",
        "border-top-left-radius": "borderTopLeftRadius",
        "border-top-right-radius": "borderTopRightRadius",
        "border-bottom-left-radius": "borderBottomLeftRadius",
        "border-bottom-right-radius": "borderBottomRightRadius",

        # Shadow (iOS)
        "box-shadow": "shadowColor",

        # Opacity
        "opacity": "opacity",
        "overflow": "overflow",
    }

    # Tailwind to RN mappings
    TAILWIND_MAP = {
        # Flexbox
        "flex": {"display": "flex"},
        "flex-row": {"flexDirection": "row"},
        "flex-col": {"flexDirection": "column"},
        "flex-wrap": {"flexWrap": "wrap"},
        "flex-nowrap": {"flexWrap": "nowrap"},
        "flex-1": {"flex": 1},
        "flex-auto": {"flexGrow": 1, "flexShrink": 1},
        "flex-initial": {"flexGrow": 0, "flexShrink": 1},
        "flex-none": {"flex": 0},

        # Justify
        "justify-start": {"justifyContent": "flex-start"},
        "justify-end": {"justifyContent": "flex-end"},
        "justify-center": {"justifyContent": "center"},
        "justify-between": {"justifyContent": "space-between"},
        "justify-around": {"justifyContent": "space-around"},
        "justify-evenly": {"justifyContent": "space-evenly"},

        # Align
        "items-start": {"alignItems": "flex-start"},
        "items-end": {"alignItems": "flex-end"},
        "items-center": {"alignItems": "center"},
        "items-baseline": {"alignItems": "baseline"},
        "items-stretch": {"alignItems": "stretch"},

        # Text align
        "text-left": {"textAlign": "left"},
        "text-center": {"textAlign": "center"},
        "text-right": {"textAlign": "right"},

        # Font weight
        "font-thin": {"fontWeight": "100"},
        "font-light": {"fontWeight": "300"},
        "font-normal": {"fontWeight": "400"},
        "font-medium": {"fontWeight": "500"},
        "font-semibold": {"fontWeight": "600"},
        "font-bold": {"fontWeight": "700"},
        "font-extrabold": {"fontWeight": "800"},
        "font-black": {"fontWeight": "900"},

        # Position
        "absolute": {"position": "absolute"},
        "relative": {"position": "relative"},

        # Overflow
        "overflow-hidden": {"overflow": "hidden"},
        "overflow-visible": {"overflow": "visible"},
        "overflow-scroll": {"overflow": "scroll"},
    }

    @classmethod
    def convert_tailwind_classes(cls, class_string: str) -> Dict[str, Any]:
        """Convert Tailwind classes to RN StyleSheet properties"""
        styles = {}
        classes = class_string.split()

        for css_class in classes:
            # Direct mapping
            if css_class in cls.TAILWIND_MAP:
                styles.update(cls.TAILWIND_MAP[css_class])
                continue

            # Dynamic values
            # Spacing: p-4, m-2, px-4, py-2, etc.
            spacing_match = re.match(r'^([mp])([xytrbl])?-(\d+(?:\.\d+)?|\[.+\])$', css_class)
            if spacing_match:
                prop_type = "padding" if spacing_match.group(1) == "p" else "margin"
                direction = spacing_match.group(2)
                value_str = spacing_match.group(3)

                # Handle custom values like [16px]
                if value_str.startswith('[') and value_str.endswith(']'):
                    value = int(re.sub(r'[^\d]', '', value_str))
                else:
                    value = int(float(value_str) * 4)

                if direction is None:
                    styles[prop_type] = value
                elif direction == 'x':
                    styles[f"{prop_type}Horizontal"] = value
                elif direction == 'y':
                    styles[f"{prop_type}Vertical"] = value
                elif direction == 't':
                    styles[f"{prop_type}Top"] = value
                elif direction == 'r':
                    styles[f"{prop_type}Right"] = value
                elif direction == 'b':
                    styles[f"{prop_type}Bottom"] = value
                elif direction == 'l':
                    styles[f"{prop_type}Left"] = value
                continue

            # Width/Height: w-full, h-screen, w-64, etc.
            size_match = re.match(r'^([wh])-(\d+|full|screen|auto|\[.+\])$', css_class)
            if size_match:
                prop = "width" if size_match.group(1) == "w" else "height"
                value_str = size_match.group(2)

                if value_str == "full":
                    styles[prop] = "100%"
                elif value_str == "screen":
                    styles[prop] = "100%"
                elif value_str == "auto":
                    styles[prop] = "auto"
                elif value_str.startswith('['):
                    value = int(re.sub(r'[^\d]', '', value_str))
                    styles[prop] = value
                else:
                    styles[prop] = int(float(value_str) * 4)
                continue

            # Text size: text-xs, text-sm, text-lg, text-xl, etc.
            text_size_map = {
                "text-xs": 12, "text-sm": 14, "text-base": 16,
                "text-lg": 18, "text-xl": 20, "text-2xl": 24,
                "text-3xl": 30, "text-4xl": 36, "text-5xl": 48
            }
            if css_class in text_size_map:
                styles["fontSize"] = text_size_map[css_class]
                continue

            # Colors: text-white, bg-black, text-gray-500, etc.
            color_match = re.match(r'^(text|bg|border)-(\w+)(?:-(\d+))?$', css_class)
            if color_match:
                prop_prefix = color_match.group(1)
                color_name = color_match.group(2)
                shade = color_match.group(3)

                color_value = cls._get_color_value(color_name, shade)
                if color_value:
                    if prop_prefix == "text":
                        styles["color"] = color_value
                    elif prop_prefix == "bg":
                        styles["backgroundColor"] = color_value
                    elif prop_prefix == "border":
                        styles["borderColor"] = color_value
                continue

            # Rounded corners: rounded, rounded-lg, rounded-full
            rounded_map = {
                "rounded-none": 0, "rounded-sm": 2, "rounded": 4,
                "rounded-md": 6, "rounded-lg": 8, "rounded-xl": 12,
                "rounded-2xl": 16, "rounded-3xl": 24, "rounded-full": 9999
            }
            if css_class in rounded_map:
                styles["borderRadius"] = rounded_map[css_class]
                continue

            # Gap: gap-2, gap-4, etc.
            gap_match = re.match(r'^gap-(\d+)$', css_class)
            if gap_match:
                styles["gap"] = int(gap_match.group(1)) * 4
                continue

        return styles

    @staticmethod
    def _get_color_value(color_name: str, shade: Optional[str]) -> Optional[str]:
        """Get color hex value from Tailwind color name"""
        # Basic colors
        basic_colors = {
            "white": "#ffffff",
            "black": "#000000",
            "transparent": "transparent",
        }

        if color_name in basic_colors:
            return basic_colors[color_name]

        # Tailwind color palette (subset)
        color_palette = {
            "gray": {
                "50": "#f9fafb", "100": "#f3f4f6", "200": "#e5e7eb",
                "300": "#d1d5db", "400": "#9ca3af", "500": "#6b7280",
                "600": "#4b5563", "700": "#374151", "800": "#1f2937",
                "900": "#111827"
            },
            "red": {
                "50": "#fef2f2", "100": "#fee2e2", "200": "#fecaca",
                "300": "#fca5a5", "400": "#f87171", "500": "#ef4444",
                "600": "#dc2626", "700": "#b91c1c", "800": "#991b1b",
                "900": "#7f1d1d"
            },
            "blue": {
                "50": "#eff6ff", "100": "#dbeafe", "200": "#bfdbfe",
                "300": "#93c5fd", "400": "#60a5fa", "500": "#3b82f6",
                "600": "#2563eb", "700": "#1d4ed8", "800": "#1e40af",
                "900": "#1e3a8a"
            },
            "green": {
                "50": "#f0fdf4", "100": "#dcfce7", "200": "#bbf7d0",
                "300": "#86efac", "400": "#4ade80", "500": "#22c55e",
                "600": "#16a34a", "700": "#15803d", "800": "#166534",
                "900": "#14532d"
            },
            "purple": {
                "50": "#faf5ff", "100": "#f3e8ff", "200": "#e9d5ff",
                "300": "#d8b4fe", "400": "#c084fc", "500": "#a855f7",
                "600": "#9333ea", "700": "#7e22ce", "800": "#6b21a8",
                "900": "#581c87"
            },
        }

        if color_name in color_palette:
            if shade and shade in color_palette[color_name]:
                return color_palette[color_name][shade]
            elif shade is None:
                return color_palette[color_name].get("500", "#6b7280")

        return None


class ReactToReactNativeConverter:
    """Convert React components to React Native"""

    # HTML to RN component mapping
    HTML_TO_RN = {
        "div": "View",
        "span": "Text",
        "p": "Text",
        "h1": "Text",
        "h2": "Text",
        "h3": "Text",
        "h4": "Text",
        "h5": "Text",
        "h6": "Text",
        "a": "TouchableOpacity",
        "button": "TouchableOpacity",
        "input": "TextInput",
        "textarea": "TextInput",
        "img": "Image",
        "ul": "View",
        "ol": "View",
        "li": "View",
        "form": "View",
        "label": "Text",
        "section": "View",
        "article": "View",
        "header": "View",
        "footer": "View",
        "nav": "View",
        "main": "View",
        "aside": "View",
    }

    def __init__(self):
        self.css_converter = CSSToStyleSheetConverter()
        self.style_counter = 0
        self.extracted_styles: Dict[str, Dict] = {}

    def convert_component(self, content: str, filename: str) -> Tuple[str, List[str]]:
        """
        Convert a React component to React Native

        Returns: (converted_content, warnings)
        """
        warnings = []
        result = content

        # Track imports needed
        rn_imports = set(["View", "Text", "StyleSheet"])

        # Convert HTML tags to RN components
        for html_tag, rn_component in self.HTML_TO_RN.items():
            # Opening tags with attributes
            pattern = rf'<{html_tag}(\s[^>]*)?>|<{html_tag}>'
            matches = re.findall(pattern, result, re.IGNORECASE)

            if matches:
                rn_imports.add(rn_component)

            # Replace opening tags
            result = re.sub(
                rf'<{html_tag}(\s)',
                f'<{rn_component}\\1',
                result,
                flags=re.IGNORECASE
            )
            result = re.sub(
                rf'<{html_tag}>',
                f'<{rn_component}>',
                result,
                flags=re.IGNORECASE
            )

            # Replace closing tags
            result = re.sub(
                rf'</{html_tag}>',
                f'</{rn_component}>',
                result,
                flags=re.IGNORECASE
            )

            # Self-closing tags
            result = re.sub(
                rf'<{html_tag}(\s[^>]*)?\/>' ,
                f'<{rn_component}\\1/>',
                result,
                flags=re.IGNORECASE
            )

        # Convert className to style
        result = self._convert_classnames(result)

        # Convert onClick to onPress
        result = re.sub(r'onClick=', 'onPress=', result)

        # Handle href (convert to onPress with Linking)
        if 'href=' in result:
            rn_imports.add("Linking")
            warnings.append(f"{filename}: href converted to onPress with Linking")

        # Convert img src to Image source
        result = re.sub(
            r'src=\{([^}]+)\}',
            r'source={{\1}}',
            result
        )
        result = re.sub(
            r'src="([^"]+)"',
            r'source={{uri: "\1"}}',
            result
        )

        # Handle input types
        if "TextInput" in rn_imports:
            rn_imports.add("TextInput")
            # Convert type="password" to secureTextEntry
            result = re.sub(
                r'type="password"',
                'secureTextEntry={true}',
                result
            )
            # Convert placeholder (same in RN)
            # Convert onChange to onChangeText
            result = re.sub(r'onChange=', 'onChangeText=', result)

        # Add ScrollView if needed for long content
        if result.count('<View') > 5:
            rn_imports.add("ScrollView")
            warnings.append(f"{filename}: Consider wrapping in ScrollView for scrollable content")

        # Generate import statement
        imports_list = sorted(list(rn_imports))
        import_statement = f"import {{ {', '.join(imports_list)} }} from 'react-native';"

        # Replace react-dom imports
        result = re.sub(
            r"import.*from\s+['\"]react-dom['\"];?",
            "",
            result
        )

        # Add RN imports
        result = re.sub(
            r"(import.*from\s+['\"]react['\"];?)",
            f"\\1\n{import_statement}",
            result
        )

        # If no react import found, add both
        if "import" not in result or "react" not in result.lower():
            result = f"import React from 'react';\n{import_statement}\n\n{result}"

        return result, warnings

    def _convert_classnames(self, content: str) -> str:
        """Convert className with Tailwind to StyleSheet"""
        # Find all className attributes
        pattern = r'className="([^"]+)"'

        def replace_classname(match):
            classes = match.group(1)
            styles = self.css_converter.convert_tailwind_classes(classes)

            if styles:
                self.style_counter += 1
                style_name = f"style{self.style_counter}"
                self.extracted_styles[style_name] = styles
                return f'style={{styles.{style_name}}}'
            return ''

        result = re.sub(pattern, replace_classname, content)

        # Add StyleSheet definition at the end if styles were extracted
        if self.extracted_styles:
            styles_code = self._generate_stylesheet()
            # Find the last export or end of file
            if "export default" in result:
                result = re.sub(
                    r'(export default \w+;?)',
                    f'{styles_code}\n\n\\1',
                    result
                )
            else:
                result += f"\n\n{styles_code}"

        return result

    def _generate_stylesheet(self) -> str:
        """Generate StyleSheet.create() code"""
        styles_obj = json.dumps(self.extracted_styles, indent=2)
        # Remove quotes from property names
        styles_obj = re.sub(r'"(\w+)":', r'\1:', styles_obj)
        return f"const styles = StyleSheet.create({styles_obj});"


class MobileExportService:
    """
    Service for exporting web projects to mobile (React Native/Expo)
    """

    def __init__(self):
        self.converter = ReactToReactNativeConverter()

    async def export_to_expo(
        self,
        files: List[SourceFile],
        project_name: str,
        use_expo_router: bool = True
    ) -> ExportResult:
        """
        Export web project to Expo

        Args:
            files: List of source files from web project
            project_name: Name for the mobile project
            use_expo_router: Use Expo Router for navigation

        Returns:
            ExportResult with converted files
        """
        try:
            converted_files = []
            warnings = []
            stats = {
                "total_files": len(files),
                "converted": 0,
                "skipped": 0,
                "warnings": 0
            }

            # Generate base Expo project files
            base_files = self._generate_expo_base_files(project_name, use_expo_router)
            converted_files.extend(base_files)

            # Process each source file
            for source_file in files:
                try:
                    converted, file_warnings = self._process_file(
                        source_file,
                        use_expo_router
                    )

                    if converted:
                        converted_files.extend(converted)
                        stats["converted"] += 1
                    else:
                        stats["skipped"] += 1

                    warnings.extend(file_warnings)
                    stats["warnings"] += len(file_warnings)

                except Exception as e:
                    warnings.append(f"Error processing {source_file.name}: {str(e)}")
                    stats["skipped"] += 1

            # Generate zip file
            zip_content = self._create_zip(converted_files)

            return ExportResult(
                success=True,
                files=converted_files,
                zip_content=zip_content,
                warnings=warnings,
                stats=stats
            )

        except Exception as e:
            logger.exception("Mobile export failed")
            return ExportResult(
                success=False,
                error=str(e)
            )

    def _generate_expo_base_files(
        self,
        project_name: str,
        use_expo_router: bool
    ) -> List[ConvertedFile]:
        """Generate base Expo project files"""
        files = []

        # package.json
        package_json = {
            "name": project_name.lower().replace(" ", "-"),
            "version": "1.0.0",
            "main": "expo-router/entry" if use_expo_router else "node_modules/expo/AppEntry.js",
            "scripts": {
                "start": "expo start",
                "android": "expo start --android",
                "ios": "expo start --ios",
                "web": "expo start --web"
            },
            "dependencies": {
                "expo": "~50.0.0",
                "expo-status-bar": "~1.11.0",
                "react": "18.2.0",
                "react-native": "0.73.2",
                "react-native-safe-area-context": "4.8.2",
                "react-native-screens": "~3.29.0"
            },
            "devDependencies": {
                "@babel/core": "^7.20.0",
                "@types/react": "~18.2.45",
                "typescript": "^5.1.3"
            },
            "private": True
        }

        if use_expo_router:
            package_json["dependencies"]["expo-router"] = "~3.4.0"
            package_json["dependencies"]["expo-linking"] = "~6.2.0"

        files.append(ConvertedFile(
            path="package.json",
            content=json.dumps(package_json, indent=2)
        ))

        # app.json (Expo config)
        app_json = {
            "expo": {
                "name": project_name,
                "slug": project_name.lower().replace(" ", "-"),
                "version": "1.0.0",
                "orientation": "portrait",
                "icon": "./assets/icon.png",
                "userInterfaceStyle": "automatic",
                "splash": {
                    "image": "./assets/splash.png",
                    "resizeMode": "contain",
                    "backgroundColor": "#ffffff"
                },
                "assetBundlePatterns": ["**/*"],
                "ios": {
                    "supportsTablet": True,
                    "bundleIdentifier": f"com.{project_name.lower().replace(' ', '')}"
                },
                "android": {
                    "adaptiveIcon": {
                        "foregroundImage": "./assets/adaptive-icon.png",
                        "backgroundColor": "#ffffff"
                    },
                    "package": f"com.{project_name.lower().replace(' ', '')}"
                },
                "web": {
                    "favicon": "./assets/favicon.png",
                    "bundler": "metro"
                },
                "scheme": project_name.lower().replace(" ", "")
            }
        }

        files.append(ConvertedFile(
            path="app.json",
            content=json.dumps(app_json, indent=2)
        ))

        # babel.config.js
        babel_config = """module.exports = function(api) {
  api.cache(true);
  return {
    presets: ['babel-preset-expo'],
  };
};
"""
        files.append(ConvertedFile(
            path="babel.config.js",
            content=babel_config
        ))

        # tsconfig.json
        tsconfig = {
            "extends": "expo/tsconfig.base",
            "compilerOptions": {
                "strict": True,
                "paths": {
                    "@/*": ["./*"]
                }
            },
            "include": ["**/*.ts", "**/*.tsx", ".expo/types/**/*.ts", "expo-env.d.ts"]
        }

        files.append(ConvertedFile(
            path="tsconfig.json",
            content=json.dumps(tsconfig, indent=2)
        ))

        # App entry point
        if use_expo_router:
            # app/_layout.tsx for Expo Router
            layout_content = """import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';

export default function RootLayout() {
  return (
    <SafeAreaProvider>
      <StatusBar style="auto" />
      <Stack
        screenOptions={{
          headerStyle: {
            backgroundColor: '#6366f1',
          },
          headerTintColor: '#fff',
          headerTitleStyle: {
            fontWeight: 'bold',
          },
        }}
      />
    </SafeAreaProvider>
  );
}
"""
            files.append(ConvertedFile(
                path="app/_layout.tsx",
                content=layout_content
            ))

            # app/index.tsx (home screen)
            index_content = """import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { Link } from 'expo-router';

export default function HomeScreen() {
  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.title}>Welcome to Your App</Text>
        <Text style={styles.subtitle}>Built with Expo</Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  content: {
    padding: 20,
    alignItems: 'center',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1e293b',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#64748b',
  },
});
"""
            files.append(ConvertedFile(
                path="app/index.tsx",
                content=index_content
            ))

        else:
            # Traditional App.tsx entry
            app_content = """import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, View, SafeAreaView } from 'react-native';

export default function App() {
  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.title}>Welcome to Your App</Text>
        <StatusBar style="auto" />
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  content: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
  },
});
"""
            files.append(ConvertedFile(
                path="App.tsx",
                content=app_content
            ))

        # .gitignore
        gitignore = """node_modules/
.expo/
dist/
npm-debug.*
*.jks
*.p8
*.p12
*.key
*.mobileprovision
*.orig.*
web-build/
.env
"""
        files.append(ConvertedFile(
            path=".gitignore",
            content=gitignore
        ))

        # README.md
        readme = f"""# {project_name}

Mobile app built with Expo.

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm start
   ```

3. Run on device/simulator:
   - Press `i` for iOS
   - Press `a` for Android
   - Press `w` for Web

## Building for Production

```bash
# Build for all platforms
npx expo build

# Or use EAS Build
npx eas build --platform all
```
"""
        files.append(ConvertedFile(
            path="README.md",
            content=readme
        ))

        return files

    def _process_file(
        self,
        source_file: SourceFile,
        use_expo_router: bool
    ) -> Tuple[List[ConvertedFile], List[str]]:
        """Process a single source file"""
        converted = []
        warnings = []

        filename = source_file.name.lower()

        # Skip non-convertible files
        skip_patterns = [
            '.css', '.scss', '.sass', '.less',  # CSS (handled inline)
            '.svg',  # SVG (needs special handling)
            'index.html', '.html',
            'vite.config', 'next.config', 'webpack.config',
            'tailwind.config', 'postcss.config',
            '.env', '.gitignore',
            'package.json', 'package-lock.json',
            'tsconfig.json', 'jsconfig.json'
        ]

        if any(pattern in filename for pattern in skip_patterns):
            return [], [f"Skipped: {source_file.name}"]

        # Convert React components
        if filename.endswith(('.tsx', '.jsx', '.ts', '.js')):
            # Reset converter state for each file
            self.converter = ReactToReactNativeConverter()

            converted_content, file_warnings = self.converter.convert_component(
                source_file.content,
                source_file.name
            )

            warnings.extend(file_warnings)

            # Determine output path
            if 'page' in filename or 'screen' in filename:
                # Page/Screen -> app/ directory for Expo Router
                if use_expo_router:
                    out_name = source_file.name.replace('Page', '').replace('Screen', '')
                    out_name = out_name.replace('.jsx', '.tsx').replace('.js', '.tsx')
                    output_path = f"app/{out_name}"
                else:
                    output_path = f"screens/{source_file.name.replace('.jsx', '.tsx').replace('.js', '.tsx')}"
            elif 'component' in filename.lower() or source_file.type == 'component':
                output_path = f"components/{source_file.name.replace('.jsx', '.tsx').replace('.js', '.tsx')}"
            elif 'hook' in filename.lower() or filename.startswith('use'):
                output_path = f"hooks/{source_file.name}"
            elif 'util' in filename.lower() or 'helper' in filename.lower():
                output_path = f"utils/{source_file.name}"
            else:
                output_path = f"src/{source_file.name.replace('.jsx', '.tsx').replace('.js', '.tsx')}"

            converted.append(ConvertedFile(
                path=output_path,
                content=converted_content,
                original=source_file.name
            ))

        return converted, warnings

    def _create_zip(self, files: List[ConvertedFile]) -> bytes:
        """Create zip archive from converted files"""
        buffer = io.BytesIO()

        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file in files:
                zf.writestr(file.path, file.content)

        buffer.seek(0)
        return buffer.read()


# Singleton instance
mobile_export_service = MobileExportService()
