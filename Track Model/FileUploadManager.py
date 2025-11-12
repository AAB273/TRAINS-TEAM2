import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk


class FileUploadManager:
    def __init__(self, data_manager, ui_reference=None):
        """
        Initialize the upload manager.

        :param data_manager: Instance of TrackDataManager (shared backend data)
        :param ui_reference: Optional reference to the TrackModelUI for UI refreshes
        """
        self.data_manager = data_manager
        self.ui_reference = ui_reference  # Optional reference for calling UI refresh methods
        self.terminals = []
    
    def upload_track_file(self):
        """Handle track file uploads (e.g., Excel or CSV) and pass to TrackDataManager."""
        from tkinter import filedialog, messagebox
        import os

        file_path = filedialog.askopenfilename(
            title="Select Track File",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if not file_path:
            return  # user canceled

        try:
            self.track_data.load_track_data(file_path)
            messagebox.showinfo("Upload Successful", f"Loaded track data from:\n{os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Upload Error", f"Could not load track file:\n{e}")


    def auto_load_green_line(self):
        """
        Automatically load the Green Line track data from 'Track Data.xlsx' if it exists in the directory.
        Reads columns for block geometry and infrastructure, then updates the TrackDataManager.
        """
        import os
        import pandas as pd
        from Track_Blocks import Block

        # Look for the Excel file in the same directory as this script
        track_file = os.path.join(os.path.dirname(__file__), "Track Data.xlsx")

        if not os.path.exists(track_file):
            print("[FileUploadManager] ⚠️ 'Track Data.xlsx' not found in directory.")
            return False

        try:
            # Load Excel sheet (Green Line)
            df = pd.read_excel(track_file, sheet_name="Green Line")
            print(f"[FileUploadManager] 📊 Loaded Excel file with columns: {list(df.columns)}")

            # --- Verify required columns ---
            required_cols = [
                "Block Number",
                "Block Length (m)",
                "Block Grade (%)",
                "ELEVATION (M)",
                "Speed Limit (Km/Hr)"
            ]
            for col in required_cols:
                if col not in df.columns:
                    raise ValueError(f"Missing required column: {col}")

            # --- Store Infrastructure info (if column exists) ---
            if "Infrastructure" in df.columns:
                self.data_manager.infrastructure_data = {
                    int(row["Block Number"]): str(row["Infrastructure"])
                    for _, row in df.iterrows()
                    if not pd.isna(row["Infrastructure"])
                }
                print(f"[FileUploadManager] 🧱 Infrastructure data loaded for "
                    f"{len(self.data_manager.infrastructure_data)} blocks.")
            else:
                self.data_manager.infrastructure_data = {}
                print("[FileUploadManager] ⚠️ No 'Infrastructure' column found in Excel.")

            # --- Load Green Line block data ---
            self.data_manager.blocks = []
            for _, row in df.iterrows():
                try:
                    block = Block(
                        block_number=int(row["Block Number"]),
                        length=float(row["Block Length (m)"]),
                        grade=float(row["Block Grade (%)"]),
                        elevation=float(row["ELEVATION (M)"]),
                        speed_limit=float(row["Speed Limit (Km/Hr)"])
                    )

                    # Attach infrastructure info if available
                    infra = self.data_manager.infrastructure_data.get(block.block_number, None)
                    if infra:
                        block.infrastructure = infra

                    self.data_manager.blocks.append(block)

                except Exception as e:
                    print(f"[FileUploadManager] ⚠️ Skipped invalid row: {e}")

            print(f"[FileUploadManager] ✅ Loaded {len(self.data_manager.blocks)} Green Line blocks successfully.")

            # --- Refresh UI if available ---
            if self.ui_reference and hasattr(self.ui_reference, "refresh_ui"):
                self.ui_reference.refresh_ui()

            return True

        except Exception as e:
            print(f"[FileUploadManager] ❌ Failed to load Green Line data: {e}")
            return False


    # ---------------- Excel / CSV / Text Upload Handlers ----------------

    def handle_data_upload(self, filename):
        """Handle Excel/TXT upload - read track data"""
        try:
            file_extension = filename.lower().split('.')[-1]
            
            if file_extension in ['xlsx', 'xls']:
                self.handle_excel_upload(filename)
            elif file_extension == 'txt':
                self.handle_text_upload(filename)
                
        except Exception as e:
            self.log_to_all_terminals(f"[ERROR] Failed to process data file: {str(e)}")
            print(f"❌ Error processing data file: {e}")

    def handle_excel_upload(self, filename):
        """Process Excel file for track data with the specific structure"""
        try:
            import pandas as pd
            
            # Read Excel file
            df = pd.read_excel(filename)
            print(f"📊 Excel file loaded with columns: {list(df.columns)}")
            print(f"📊 First few rows:\n{df.head()}")
            
            # Process the specific structure
            self.process_structured_track_data(df)
            
            self.log_to_all_terminals(f"[SUCCESS] Excel data loaded from: {filename.split('/')[-1]}")
            
        except Exception as e:
            self.log_to_all_terminals(f"[ERROR] Excel processing failed: {str(e)}")
            print(f"❌ Excel processing error: {e}")

    def handle_text_upload(self, filename):
        """Process text file for track data — supports CSV or delimited formats."""
        try:
            # Try CSV first
            try:
                df = pd.read_csv(filename)
                print(f"📊 CSV file loaded with columns: {list(df.columns)}")
                self.process_structured_track_data(df)
                self._log_success(filename, "CSV")
                return
            except Exception:
                pass

            # Try whitespace-delimited
            try:
                df = pd.read_csv(filename, delim_whitespace=True)
                print(f"📊 Text file loaded with columns: {list(df.columns)}")
                self.process_structured_track_data(df)
                self._log_success(filename, "Text")
                return
            except Exception:
                pass

            # Fallback: manually parse text
            with open(filename, "r") as file:
                lines = file.readlines()

            track_data = self.parse_text_track_data(lines)
            self.process_track_data(track_data)
            self._log_success(filename, "Raw Text")

        except Exception as e:
            self._log_error("Text", e)

    # ---------------- Data Processing Core ----------------

    def process_structured_track_data(self, df):
        """Update track blocks from structured DataFrame."""
        for index, row in df.iterrows():
            if index < len(self.data_manager.blocks):
                block = self.data_manager.blocks[index]
                if "Block Grade (%)" in df.columns:
                    block.grade = float(row["Block Grade (%)"])
                if "ELEVATION (M)" in df.columns:
                    block.elevation = float(row["ELEVATION (M)"])
                if "Block Length (m)" in df.columns:
                    block.length = float(row["Block Length (m)"])
                if "Speed Limit (Km/Hr)" in df.columns:
                    block.speed_limit = float(row["Speed Limit (Km/Hr)"])
                print(f"📝 Updated block {block.block_number}: Grade={block.grade}%, Elevation={block.elevation}m")

        # Refresh UI if linked
        if self.ui_reference and hasattr(self.ui_reference, "refresh_ui"):
            self.ui_reference.refresh_ui()

    # def handle_text_upload(self, filename):
    #     """Process text file for track data"""
    #     try:
    #         with open(filename, 'r') as file:
    #             lines = file.readlines()
            
    #         # Parse text data - look for common track data patterns
    #         track_data = self.parse_text_track_data(lines)
            
    #         # Process the extracted data
    #         self.process_track_data(track_data)
            
    #         self.log_to_all_terminals(f"[SUCCESS] Text data loaded from: {filename.split('/')[-1]}")
            
    #     except Exception as e:
    #         self.log_to_all_terminals(f"[ERROR] Text processing failed: {str(e)}")
    #         print(f"❌ Text processing error: {e}")

    def parse_text_track_data(self, lines):
        """Parse raw text into structured dictionary form."""
        data = {}
        current_section = None

        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if (
                ":" in line
                or line.endswith("(%)")
                or any(keyword in line for keyword in ["Grade", "Elevation", "Length", "Speed", "Block"])
            ):
                current_section = line.split(":")[0].strip()
                data[current_section] = []
                continue

            if current_section and line.replace(".", "").replace("-", "").isdigit():
                try:
                    value = float(line)
                    data[current_section].append(value)
                except ValueError:
                    continue

        return data

    def process_track_data(self, data):
        """Process either DataFrame or dict input and update the blocks accordingly."""
        try:
            if hasattr(data, "columns"):
                self.process_dataframe(data)
            elif isinstance(data, dict):
                self.process_data_dict(data)

            if self.ui_reference and hasattr(self.ui_reference, "refresh_ui"):
                self.ui_reference.refresh_ui()

        except Exception as e:
            print(f"❌ Error processing track data: {e}")

    def process_dataframe(self, df):
        """Process and apply updates from a DataFrame."""
        for index, row in df.iterrows():
            if index < len(self.data_manager.blocks):
                block = self.data_manager.blocks[index]
                if "Block Grade (%)" in df.columns:
                    block.grade = float(row["Block Grade (%)"])
                if "ELEVATION (M)" in df.columns:
                    block.elevation = float(row["ELEVATION (M)"])
                if "Block Length (m)" in df.columns:
                    block.length = float(row["Block Length (m)"])
                if "Speed Limit (Km/Hr)" in df.columns:
                    block.speed_limit = float(row["Speed Limit (Km/Hr)"])
                print(f"📝 Updated block {block.block_number}: Grade={block.grade}%, Elevation={block.elevation}m")

    def process_data_dict(self, data_dict):
        """Process dictionary-based track data."""
        print(f"📋 Processing data dictionary: {list(data_dict.keys())}")
        if "Block Grade (%)" in data_dict:
            grades = data_dict["Block Grade (%)"]
            for i, grade in enumerate(grades):
                if i < len(self.data_manager.blocks):
                    self.data_manager.blocks[i].grade = grade
                    print(f"📝 Set block {i+1} grade to: {grade}%")

    # ---------------- Logging Utilities ----------------

    def _log_success(self, filename, filetype):
        if self.ui_reference and hasattr(self.ui_reference, "log_to_all_terminals"):
            self.ui_reference.log_to_all_terminals(f"[SUCCESS] {filetype} data loaded from: {filename.split('/')[-1]}")
        print(f"✅ {filetype} data successfully loaded from {filename}")

    def _log_error(self, filetype, error):
        if self.ui_reference and hasattr(self.ui_reference, "log_to_all_terminals"):
            self.ui_reference.log_to_all_terminals(f"[ERROR] {filetype} processing failed: {str(error)}")
        print(f"❌ {filetype} processing error: {error}")
