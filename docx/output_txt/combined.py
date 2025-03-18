import os

def combine_text_files(output_file):
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for file in os.listdir(os.getcwd()):
            if file.endswith('.txt') and file != output_file:
                try:
                    with open(file, 'r', encoding='utf-8') as infile:
                        outfile.write(f"\n--- {file} ---\n")  # Add a separator with the filename
                        outfile.write(infile.read())
                        outfile.write("\n")  # Add a newline for separation
                    print(f"Added {file} to {output_file}")
                except Exception as e:
                    print(f"Failed to read {file}: {e}")

if __name__ == "__main__":
    output_file = "combined_output.txt"  # Name of the combined file
    combine_text_files(output_file)
    print(f"\nCombined text saved to: {output_file}")
