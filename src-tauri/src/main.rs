#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri::Manager;

fn main() {
    tauri::Builder::default()
        .setup(|app| {
            let window = app.get_webview_window("main").unwrap();

            // macOS: set transparent background + mouse passthrough for empty areas
            #[cfg(target_os = "macos")]
            {
                use tauri::LogicalSize;
                window.set_size(LogicalSize::new(300.0, 300.0)).ok();
                window.set_ignore_cursor_events(false).ok();
            }

            // Windows: layered window transparency
            #[cfg(target_os = "windows")]
            {
                window.set_ignore_cursor_events(false).ok();
            }

            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("启动失败");
}
