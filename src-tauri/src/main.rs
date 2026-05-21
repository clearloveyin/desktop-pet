#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri::Manager;

fn main() {
    tauri::Builder::default()
        .setup(|app| {
            let window = app.get_webview_window("main").unwrap();

            // Retain cursor events for pet interaction
            #[cfg(target_os = "macos")]
            {
                window.set_ignore_cursor_events(false).ok();
            }
            #[cfg(target_os = "windows")]
            {
                window.set_ignore_cursor_events(false).ok();
            }

            // Close window to tray instead of quitting
            let win = window.clone();
            window.on_window_event(move |event| {
                if let tauri::WindowEvent::CloseRequested { .. } = event {
                    win.hide().ok();
                }
            });

            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("启动失败");
}
