from selenium import webdriver
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
import time

# Set up the WebDriver using WebDriverManager
driver = webdriver.Chrome(ChromeDriverManager().install())

try:
    # Open the target website
    driver.get("http://192.168.2.28/GMPS_V2/examples/MFT_DLL_VERSION_v6.php")
    
    # Wait for the page to load
    time.sleep(3)

    # Select dropdown by name "Repo" and choose the 2nd option (index 1)
    repo_dropdown = Select(driver.find_element("name", "Repo"))
    repo_dropdown.select_by_index(1)

    # Select dropdown by name "Project_Name" and choose the 1st option (index 0)
    project_name_dropdown = Select(driver.find_element("name", "Project_Name"))
    project_name_dropdown.select_by_index(0)

    # Select dropdown by name "branch" and choose the 3rd option (index 2)
    branch_dropdown = Select(driver.find_element("name", "branch"))
    branch_dropdown.select_by_index(2)

    # Pause to observe
    time.sleep(5)

finally:
    # Close the browser
    driver.quit()
