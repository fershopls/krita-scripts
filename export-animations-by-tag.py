import krita
from time import sleep
from krita import InfoObject
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QFileDialog

EXPORT_SUBJECT = r""
EXPORT_DIRECTORY = r""

def create_file():
    # Get the Krita instance
    krita_instance = krita.Krita.instance()
    
    # Open a file dialog to create a new file
    # png
    file_path, _ = QFileDialog.getSaveFileName(
        None,
        "Create New File",
        "",
        "PNG Files (*.png);;All Files (*)"
    )
    
    # Check if a file path was specified
    if file_path:
        # Create an empty file
        try:
            print(f"File select: {file_path}")
            return file_path
        except IOError as e:
            print(f"Error select file: {e}")
            return None
    else:
        print("File select cancelled")
        return None

#
# BEFORE SCRIPT
#
if not EXPORT_SUBJECT or not EXPORT_DIRECTORY:
    import os
    output_filepath = create_file()

    if not output_filepath:
        print("No output file selected.")
        exit()

    output_directory = os.path.dirname(output_filepath)
    output_filename_with_extension = os.path.basename(output_filepath)
    output_filename_without_extension = os.path.splitext(output_filename_with_extension)[0]

    EXPORT_SUBJECT = output_filename_without_extension
    EXPORT_DIRECTORY = output_directory

def select_directory():
    # Get the Krita instance
    krita_instance = krita.Krita.instance()
    
    # Open a file dialog to select a directory
    directory = QFileDialog.getExistingDirectory(
        None,
        "Select Directory",
        "",
        QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
    )
    
    # Check if a directory was selected
    if directory:
        print(f"Selected directory: {directory}")
        return directory
    else:
        print("No directory selected")
        return None

def main():
    # Get the active document
    document = Krita.instance().activeDocument()

    if not document:
        print("No active document found.")
        return

    # Get all layers in the document
    root_node = document.rootNode()
    root_layers = root_node.childNodes()

    # Hide all layers
    initial_current_time = document.currentTime()
    initial_layers_visible = [layer.visible() for layer in root_layers]
    for layer in root_layers:
        layer.setVisible(False)
    
    # Export each layer
    for layer in root_layers:
        if layer.name().endswith("-hide"):
            layer.setVisible(False)

            continue

        if layer.type() == "grouplayer":
            print(f"Layer {layer.name()} is a group layer.")
            layer.setVisible(True)
            export_frames(document, layer.name())
            layer.setVisible(False)
            continue
            
        if not layer.animated():
            print(f"Layer {layer.name()} is not animated.")
            continue

        layer.setVisible(True)
        export_frames(document, layer.name())
        layer.setVisible(False)
    
    print("Exported all frames.")

    # Restore the initial visibility of the layers
    for i, layer in enumerate(root_layers):
        layer.setVisible(initial_layers_visible[i])
    
    # Restore the initial current time
    document.setCurrentTime(initial_current_time)

def export_frames(document, layer_name):
    print(f"Exporting layer {layer_name}...")
    
    frames_count = document.animationLength()
    for i in range(frames_count):
        document.setCurrentTime(i)
        
        # grab the byte array data and show the data that it is storing
        pixelBytes = document.pixelData(0, 0, document.width(), document.height())
        
        # check if the pixel data is empty
        is_image_empty = True
        image_bytes = 0
        for byte in pixelBytes:
            if byte != b'\x00':
                is_image_empty = False
                image_bytes += 1
                print(f"Byte: {byte}")
            
            if image_bytes > 100:
                break
        
        if is_image_empty:
            print(f"Layer {layer_name} frame {i} is empty.")
            break

        # Set up export configuration
        info = InfoObject()
        info.setProperty("alpha", True)
        info.setProperty("compression", 3)
        info.setProperty("forceSRGB", False)
        info.setProperty("indexed", False)
        info.setProperty("interlaced", False)
        info.setProperty("saveSRGBProfile", False)
        info.setProperty("transparencyFillcolor", [0, 0, 0, 0])

        # Set the filename
        filename = f"{EXPORT_SUBJECT}-{layer_name}-{i}"
        filepath = f"{EXPORT_DIRECTORY}/{filename}.png"
        
        # Export the document
        document.setBatchmode(True)
        document.exportImage(filepath, info)
        
        print(f"Exported: {filepath}")

main()
