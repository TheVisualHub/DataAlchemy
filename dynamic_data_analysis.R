# Dynamic Data Analysis in R (ver 1.1 betta):
# This is the R adaptation of my python script made during my PhD
# to visualize the fractional variance of individual Principal Components
# calculated from molecualar dynamics data using GROMACS.
# For integrative visualization this data pipeline process All input data files
# and creates 2D and 3D visualizations of the whole data 
# Designed, programmed and benchmarked by Gleb Novikov,
# The Visual Hub - All rights reserved - 2025

# Load necessary R libraries
library(tools) # For file path handling functions
library(ggplot2)  # For basic plotting
library(plotly) # For advanced plotting

# Main configuration
input_directory <- "./xvg_PCA"  # Change this path to your directory
output_directory <- "./xvg_with_percents"  # Directory where you want to save the output files
log_file_path <- "./variance_PCs.txt"
plot_output_path <- "./3d_histogram.html"  # Path to save the 3D histograms

# Create the output directory if it does not exist
# simple directory checking like os/shutil in python ..
if (!dir.exists(output_directory)) {
  dir.create(output_directory)
}

# Introduce a list of ALL .xvg files in the input directory
xvg_files <- list.files(input_directory, pattern = "\\.xvg$", full.names = TRUE)


#--- Main functions ---#
# Function to parse and process a single .xvg file with PC fractions
process_xvg_file <- function(file_path) {
  # Read the file as text lines
  lines <- readLines(file_path)
  
  # Identify the starting line of numeric data
  data_start <- grep("^\\s*\\d", lines)[1]
  
  # Read the data from the identified start line onwards
  data_clean <- read.table(text = lines[data_start:length(lines)], stringsAsFactors = FALSE)
  
  # Convert the relevant columns to numeric
  data_clean$V1 <- as.numeric(data_clean$V1)
  data_clean$V2 <- as.numeric(data_clean$V2)
  
  # Calculate the total sum of Y values
  total_sum <- sum(data_clean$V2, na.rm = TRUE)
  
  # Convert Y values to percentages
  data_clean$Y_percentage <- (data_clean$V2 / total_sum) * 100
  
  # Generate output file name
  output_file_name <- file_path_sans_ext(basename(file_path))
  output_file <- file.path(output_directory, paste0(output_file_name, "_perc.txt"))
  
  # Save the output to a new file
  write.table(data_clean, file = output_file, row.names = FALSE, col.names = FALSE)
  
  return(output_file) # Return the path to the generated output file
}

# Apply the processing function to each .xvg file and collect the output file paths
output_files <- lapply(xvg_files, process_xvg_file)

# Open the final log file for writing
log_connection <- file(log_file_path, open = "w")

# Function to extract and log the first 5 samples from each xvg
# We consider only first 5 principal components
# as they usually represent the largest fraction of the data variance
log_first_5_samples <- function(output_file) {
  # Read the processed data
  processed_data <- read.table(output_file, header = FALSE)
  
  # Extract the first 5 rows and the relevant columns (X = V1, Y_percentage = V3)
  sample_data <- processed_data[1:5, c(1, 3)]
  
  # Write the file name before the data
  cat("File:", output_file, "\n", file = log_connection, append = TRUE)
  
  # Write the sample data to the log file
  write.table(sample_data, file = log_connection, row.names = FALSE, col.names = FALSE, append = TRUE)

  # Add a new line for separation
  cat("\n\n", file = log_connection, append = TRUE)
}

# Apply the previous function to each XVG file
lapply(output_files, log_first_5_samples)

# Close the log file
close(log_connection)

cat("Processing and logging completed. The final log is saved at:", log_file_path, "\n")

########### DATA VIZUALIZATION ##############

# Print data with corresponded percentages
print_percentage_data <- function(output_file) {
  # Read the processed data
  processed_data <- read.table(output_file, header = FALSE)
  
  # Print the data with percentages
  print(processed_data)
}

# Apply the print function to each file
lapply(output_files, print_percentage_data)

# Prepare data for plotting
all_data <- do.call(rbind, lapply(output_files, function(file) {
  data <- read.table(file, header = FALSE)
  data <- head(data, 10)  # Select the first 10 samples
  data$file <- basename(file)  # Add a column with the file name (Z-axis)
  return(data)
}))

all_data$file <- gsub("_perc.txt", "", all_data$file)

# craft 2D Plot using ggplot2
ggplot(all_data, aes(x = round(V1), y = V3, color = file, group = file)) +
  geom_point(size = 2.0) +
  geom_line(linewidth = 0.6) +
  scale_x_continuous(breaks = 1:10, labels = 1:10) +  # X-axis with integers only
  labs(title = "Contribtion of the individuals PCs to the dynamics", 
       x = "Principal Components (1-10)", 
       y = "Contribution to dynamics (%)", 
       color = "Replicas:") +
  theme_minimal() +
   theme(
    axis.title.x = element_text(size = 14),   # Set X axis title font size
    axis.title.y = element_text(size = 14),   # Set Y axis title font size
    axis.text.x = element_text(size = 12),    # Set X axis tick labels font size
    axis.text.y = element_text(size = 12),     # Set Y axis tick labels font size
    legend.position = "top",               # Move legend to the bottom
    legend.title = element_text(size = 12),   # Set legend title size
    legend.text = element_text(size = 10),    # Set legend text size
    #legend.background = element_rect(fill = "gray90", color = "black"),  # Add background and border to legend
    legend.key = element_rect(fill = "white", color = NA)  # Set legend key background to white
  )

# Additionally make a 3D data visualization
# Prepare data for the 3D histogram
all_data$Z <- as.factor(all_data$file)  # Convert file names to factor (for Z-axis)

# Create a 3D plot using plotly
fig <- plot_ly(
  data = all_data,
  x = ~round(V1),
  y = ~V3,
  z = ~as.numeric(Z),
  type = "scatter3d",
  mode = "markers",
  marker = list(size = 5, color = ~as.numeric(Z), colorscale = "Viridis")
)

# Customize the layout for better visualization
fig <- fig %>% layout(
  scene = list(
    xaxis = list(title = "Principal Components (1-10)"),
    yaxis = list(title = "Contribution to dynamics (%)"),
    zaxis = list(title = "Source File"),
    aspectmode = "cube"  # To keep all axes proportional
  ),
  title = "3D Histogram of Overlapped Data from Multiple Files"
)

# Save the plot as an HTML file
htmlwidgets::saveWidget(fig, file = plot_output_path)