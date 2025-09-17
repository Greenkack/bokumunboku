// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::process::{Command, Stdio};
use std::thread;
use std::time::Duration;
use tauri::{CustomMenuItem, Menu, MenuItem, Submenu, SystemTray, SystemTrayEvent, SystemTrayMenu, WindowBuilder, WindowUrl};

// Tauri commands for backend communication
#[tauri::command]
fn start_backend() -> Result<String, String> {
    // Start FastAPI backend server
    thread::spawn(|| {
        let output = Command::new("python")
            .args(["-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000"])
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .spawn();
            
        match output {
            Ok(mut child) => {
                let _ = child.wait();
            }
            Err(e) => {
                eprintln!("Failed to start backend: {}", e);
            }
        }
    });
    
    // Wait a moment for server to start
    thread::sleep(Duration::from_secs(2));
    
    Ok("Backend started".to_string())
}

#[tauri::command]
fn check_backend_health() -> Result<bool, String> {
    // Simple health check for backend
    let output = Command::new("curl")
        .args(["-s", "-o", "/dev/null", "-w", "%{http_code}", "http://localhost:8000/health"])
        .output();
        
    match output {
        Ok(output) => {
            let status_code = String::from_utf8_lossy(&output.stdout);
            Ok(status_code == "200")
        }
        Err(_) => Ok(false)
    }
}

#[tauri::command]
fn open_pdf(path: String) -> Result<(), String> {
    // Open PDF with system default application
    #[cfg(target_os = "windows")]
    {
        Command::new("cmd")
            .args(["/C", "start", "", &path])
            .spawn()
            .map_err(|e| e.to_string())?;
    }
    
    #[cfg(target_os = "macos")]
    {
        Command::new("open")
            .arg(&path)
            .spawn()
            .map_err(|e| e.to_string())?;
    }
    
    #[cfg(target_os = "linux")]
    {
        Command::new("xdg-open")
            .arg(&path)
            .spawn()
            .map_err(|e| e.to_string())?;
    }
    
    Ok(())
}

#[tauri::command]
fn save_file_dialog() -> Result<Option<String>, String> {
    use tauri::api::dialog::FileDialogBuilder;
    
    let (tx, rx) = std::sync::mpsc::channel();
    
    FileDialogBuilder::new()
        .set_title("PDF speichern unter...")
        .add_filter("PDF Files", &["pdf"])
        .save_file(move |path| {
            tx.send(path).unwrap();
        });
    
    match rx.recv() {
        Ok(Some(path)) => Ok(Some(path.to_string_lossy().to_string())),
        Ok(None) => Ok(None),
        Err(_) => Err("Dialog error".to_string())
    }
}

fn main() {
    // Create system tray menu
    let quit = CustomMenuItem::new("quit".to_string(), "Beenden");
    let show = CustomMenuItem::new("show".to_string(), "Anzeigen");
    let tray_menu = SystemTrayMenu::new()
        .add_item(show)
        .add_native_item(tauri::SystemTrayMenuItem::Separator)
        .add_item(quit);
    
    let system_tray = SystemTray::new().with_menu(tray_menu);
    
    // Create application menu
    let submenu = Submenu::new("Solar Configurator", Menu::new()
        .add_native_item(MenuItem::About("Solar Configurator".to_string(), tauri::AboutMetadata::default()))
        .add_native_item(MenuItem::Separator)
        .add_native_item(MenuItem::Services)
        .add_native_item(MenuItem::Separator)
        .add_native_item(MenuItem::Hide)
        .add_native_item(MenuItem::HideOthers)
        .add_native_item(MenuItem::ShowAll)
        .add_native_item(MenuItem::Separator)
        .add_native_item(MenuItem::Quit));
    
    let file_menu = Submenu::new("Datei", Menu::new()
        .add_item(CustomMenuItem::new("new_project", "Neues Projekt"))
        .add_item(CustomMenuItem::new("open_project", "Projekt öffnen"))
        .add_item(CustomMenuItem::new("save_project", "Projekt speichern"))
        .add_native_item(MenuItem::Separator)
        .add_item(CustomMenuItem::new("export_pdf", "PDF exportieren"))
        .add_native_item(MenuItem::Separator)
        .add_native_item(MenuItem::Quit));
    
    let edit_menu = Submenu::new("Bearbeiten", Menu::new()
        .add_native_item(MenuItem::Undo)
        .add_native_item(MenuItem::Redo)
        .add_native_item(MenuItem::Separator)
        .add_native_item(MenuItem::Cut)
        .add_native_item(MenuItem::Copy)
        .add_native_item(MenuItem::Paste)
        .add_native_item(MenuItem::SelectAll));
    
    let view_menu = Submenu::new("Ansicht", Menu::new()
        .add_item(CustomMenuItem::new("input_view", "Eingabe"))
        .add_item(CustomMenuItem::new("analysis_view", "Analyse"))
        .add_item(CustomMenuItem::new("pdf_view", "PDF-Generierung"))
        .add_item(CustomMenuItem::new("admin_view", "Administration"))
        .add_item(CustomMenuItem::new("crm_view", "CRM")));
    
    let help_menu = Submenu::new("Hilfe", Menu::new()
        .add_item(CustomMenuItem::new("about", "Über Solar Configurator"))
        .add_item(CustomMenuItem::new("documentation", "Dokumentation"))
        .add_item(CustomMenuItem::new("support", "Support")));
    
    let menu = Menu::new()
        .add_submenu(submenu)
        .add_submenu(file_menu)
        .add_submenu(edit_menu)
        .add_submenu(view_menu)
        .add_submenu(help_menu);

    tauri::Builder::default()
        .menu(menu)
        .system_tray(system_tray)
        .on_system_tray_event(|app, event| match event {
            SystemTrayEvent::LeftClick {
                position: _,
                size: _,
                ..
            } => {
                let window = app.get_window("main").unwrap();
                window.show().unwrap();
                window.set_focus().unwrap();
            }
            SystemTrayEvent::RightClick {
                position: _,
                size: _,
                ..
            } => {
                println!("system tray received a right click");
            }
            SystemTrayEvent::DoubleClick {
                position: _,
                size: _,
                ..
            } => {
                println!("system tray received a double click");
            }
            SystemTrayEvent::MenuItemClick { id, .. } => match id.as_str() {
                "quit" => {
                    std::process::exit(0);
                }
                "show" => {
                    let window = app.get_window("main").unwrap();
                    window.show().unwrap();
                    window.set_focus().unwrap();
                }
                _ => {}
            },
            _ => {}
        })
        .on_menu_event(|event| {
            match event.menu_item_id() {
                "new_project" => {
                    // Emit event to frontend
                    event.window().emit("menu_action", "new_project").unwrap();
                }
                "open_project" => {
                    event.window().emit("menu_action", "open_project").unwrap();
                }
                "save_project" => {
                    event.window().emit("menu_action", "save_project").unwrap();
                }
                "export_pdf" => {
                    event.window().emit("menu_action", "export_pdf").unwrap();
                }
                "input_view" => {
                    event.window().emit("navigate", "/input").unwrap();
                }
                "analysis_view" => {
                    event.window().emit("navigate", "/analysis").unwrap();
                }
                "pdf_view" => {
                    event.window().emit("navigate", "/pdf").unwrap();
                }
                "admin_view" => {
                    event.window().emit("navigate", "/admin").unwrap();
                }
                "crm_view" => {
                    event.window().emit("navigate", "/crm").unwrap();
                }
                "about" => {
                    event.window().emit("menu_action", "about").unwrap();
                }
                _ => {}
            }
        })
        .invoke_handler(tauri::generate_handler![
            start_backend,
            check_backend_health,
            open_pdf,
            save_file_dialog
        ])
        .setup(|app| {
            // Start backend automatically
            let _backend_result = start_backend();
            
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}