import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

URL = "https://www.saucedemo.com"


@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_experimental_option("prefs", {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.password_manager_leak_detection": False,
    })
    d = webdriver.Chrome(options=options)
    d.maximize_window()
    d.get(URL)
    yield d
    d.quit()


def wait_for(driver, locator):
    return WebDriverWait(driver, 10).until(EC.visibility_of_element_located(locator))


def click(driver, locator):
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(locator)).click()


def login(driver, user="standard_user", pwd="secret_sauce", expect_success=True):
    wait_for(driver, (By.ID, "user-name")).send_keys(user)
    driver.find_element(By.ID, "password").send_keys(pwd)
    click(driver, (By.ID, "login-button"))
    if expect_success:
        WebDriverWait(driver, 10).until(EC.url_contains("/inventory.html"))
        wait_for(driver, (By.CLASS_NAME, "inventory_item"))


# TC01: Đăng nhập thành công
def test_login_success(driver):
    login(driver)
    assert "/inventory.html" in driver.current_url
    assert wait_for(driver, (By.CLASS_NAME, "title")).text == "Products"


# TC02: Đăng nhập sai mật khẩu -> báo lỗi
def test_login_wrong_password(driver):
    login(driver, pwd="sai_mat_khau", expect_success=False)
    err = wait_for(driver, (By.CSS_SELECTOR, "[data-test='error']")).text
    assert "Username and password do not match" in err


# TC03: Thêm sản phẩm vào giỏ hàng
def test_add_to_cart(driver):
    login(driver)
    click(driver, (By.ID, "add-to-cart-sauce-labs-backpack"))
    badge = wait_for(driver, (By.CLASS_NAME, "shopping_cart_badge"))
    assert badge.text == "1"
    click(driver, (By.CLASS_NAME, "shopping_cart_link"))
    WebDriverWait(driver, 10).until(EC.url_contains("/cart.html"))
    assert "Sauce Labs Backpack" in wait_for(driver, (By.CLASS_NAME, "inventory_item_name")).text


# TC04: Sắp xếp sản phẩm theo giá thấp -> cao
def test_sort_price_low_to_high(driver):
    login(driver)
    Select(wait_for(driver, (By.CLASS_NAME, "product_sort_container"))).select_by_value("lohi")
    prices = [float(p.text.replace("$", ""))
              for p in driver.find_elements(By.CLASS_NAME, "inventory_item_price")]
    assert prices == sorted(prices)


# TC05: Xóa sản phẩm khỏi giỏ hàng
def test_remove_from_cart(driver):
    login(driver)
    click(driver, (By.ID, "add-to-cart-sauce-labs-bike-light"))
    click(driver, (By.CLASS_NAME, "shopping_cart_link"))
    WebDriverWait(driver, 10).until(EC.url_contains("/cart.html"))
    wait_for(driver, (By.CLASS_NAME, "cart_item"))
    click(driver, (By.ID, "remove-sauce-labs-bike-light"))
    WebDriverWait(driver, 10).until(
        EC.invisibility_of_element_located((By.CLASS_NAME, "cart_item"))
    )
    assert len(driver.find_elements(By.CLASS_NAME, "cart_item")) == 0


# TC06: Đăng xuất
def test_logout(driver):
    login(driver)
    click(driver, (By.ID, "react-burger-menu-btn"))
    click(driver, (By.ID, "logout_sidebar_link"))
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "login-button")))
    assert driver.current_url.rstrip("/") == URL