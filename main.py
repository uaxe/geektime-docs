import base64
import html
import json
import os
import shutil
import subprocess
import sys
import re
import tempfile
import time
import traceback
import click
import yaml
import requests

from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import staleness_of
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.download_manager import WDMDownloadManager
from selenium.webdriver.common.by import By
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from pypdf import PdfWriter, PdfReader
from compress import __compress



requests.adapters.DEFAULT_RETRIES = 5
reqsession = requests.session()
requests.packages.urllib3.disable_warnings()
reqsession.keep_alive = False
reqsession.verify = False

retry_strategy = Retry(
    total=3,
    status_forcelist=[500, 502, 503, 504, 404],
    allowed_methods=["HEAD", "GET", "OPTIONS", "POST"],
    backoff_factor=0.5,
)

http_adapter = HTTPAdapter(
    max_retries=retry_strategy,
    pool_connections=200,
    pool_maxsize=200,
)
reqsession.mount("http://", http_adapter)
reqsession.mount("https://", http_adapter)

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
    "image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
}

def __send_devtools(driver, cmd, params={}):
    resource = "/session/%s/chromium/send_command_and_get_result" % driver.session_id
    url = f"{driver.command_executor._client_config.remote_server_addr}{resource}"
    body = json.dumps({"cmd": cmd, "params": params})
    response = driver.command_executor._request("POST", url, body)

    if not response:
        raise Exception(response.get("value"))

    return response.get("value")

def worker(driver, uri, timeout):
    driver.get(uri)
    print(f'Working on {uri}, timeout: {timeout}')

    driver.implicitly_wait(timeout)
    temp_height = 0
    while True:
        driver.execute_script("window.scrollBy(0,100)")
        check_height = driver.execute_script(
            "return document.documentElement.scrollTop || window.pageYOffset || document.body.scrollTop;",
        )
        if check_height == temp_height:
            break
        temp_height = check_height
        driver.implicitly_wait(timeout)

    driver.implicitly_wait(timeout)
    try:
        WebDriverWait(driver, timeout).until(
            staleness_of(driver.find_element(by=By.TAG_NAME, value="html")),
        )
    except TimeoutException:
        calculated_print_options = {
            "landscape": False,
            "displayHeaderFooter": False,
            "printBackground": True,
            "preferCSSPageSize": True,
        }
        result = __send_devtools(
            driver,
            "Page.printToPDF",
            calculated_print_options,
        )
        return base64.b64decode(result["data"])

def http_head(uri, timeout) -> None:
    try:
        resp = requests.head(uri, timeout=timeout, headers={'User-Agent': 'Mozilla/5.0'})
        print(f'head status_code: {resp.status_code}, {uri}')
    except Exception as e:
        print(f'head error: {e}, {uri}')

def http_get_base64(uri, timeout) -> (str, str):
    resp = requests.get(uri, timeout=timeout, headers={'User-Agent': 'Mozilla/5.0'})
    if resp.status_code != 200:
        print(f'head status_code: {resp.status_code}, {uri}')
        return None, None
    return base64.b64encode(resp.content).decode('utf8'), uri

@click.command("all_pdf")
@click.option(
    "-i",
    "--source",
    required=True,
    help="source is path",
)
@click.option(
    "-o",
    "--output",
    default=os.getcwd(),
    help="output is dir",
)
@click.option(
    "-t",
    "--timeout",
    type=int,
    default=9,
    help="get url with browser timeout",
)
@click.option(
    "-c",
    "--compress",
    type=bool,
    default=False,
    help="PDF is compressed or not. Default value is False",
)
@click.option(
    "-p",
    "--power",
    type=int,
    default=0,
    help="power of the compression. Default value is 0. This can be 0: default, 1: prepress, 2: printer, 3: ebook, 4: screen",
)
@click.option(
    "-a",
    "--port",
    type=int,
    default=8000,
    help="mkdocs port. Default value is 8000",
)
def make_all_pdf(source, output, timeout, compress, power, port):
    webdriver_options = Options()
    webdriver_prefs = {
        'profile.default_content_setting_values': {
            'notifications': 2
        }
    }
    webdriver_options.add_argument("--headless")
    webdriver_options.add_argument("--disable-gpu")
    webdriver_options.add_argument("--no-sandbox")
    webdriver_options.add_argument("--disable-dev-shm-usage")
    webdriver_options.experimental_options["prefs"] = webdriver_prefs
    webdriver_options.add_experimental_option("excludeSwitches", ['enable-automation'])

    http_client = requests.Session()
    http_client.proxies = {
        "http": "http://127.0.0.1:1087",
        "https": "http://127.0.0.1:1087",
    }
    download_manager = WDMDownloadManager(http_client=http_client)
    service = Service(ChromeDriverManager(download_manager=download_manager).install())
    host = f"http://127.0.0.1:{port}/"
    for dirname, _, file_lst in os.walk(source):
        for fname in file_lst:
            if not fname in ["mkdocs.yml"]:
                continue

            for i in range(9):
                os.popen("lsof -i:"+str(port)+" | grep -v 'PID' | awk '{print $2}' |  xargs kill -9")
                driver = webdriver.Chrome(service=service, options=webdriver_options)
                try:
                    parts_dir = os.path.join(dirname, "parts")
                    part_dir = os.path.join(parts_dir, os.path.basename(dirname))
                    if not os.path.exists(part_dir):
                        os.makedirs(part_dir, exist_ok=True)
                    pattern = r'https?://[^\s]+'
                    fpath = os.path.join(dirname, "mkdocs.yml")
                    data = yaml.safe_load(open(fpath))
                    print(f'dirname: {dirname}')
                    with tempfile.TemporaryDirectory() as tmpdir:
                        shutil.copytree(dirname, tmpdir, dirs_exist_ok=True)
                        for nav in data.get('nav'):
                            if not isinstance(nav, str):
                                raise ValueError(dirname + nav)
                            base_name = os.path.splitext(nav)[0]
                            target = os.path.join(part_dir, base_name.replace("%", "") + ".pdf")
                            if os.path.exists(target) and round(os.path.getsize(target)/1024, 2) > 10:
                                verifyImage = True
                                for page in PdfReader(target).pages:
                                    if not verifyImage:
                                        break
                                    for img in page.images:
                                        if img.image.size == (28, 32):
                                            print(f'image not verify: {target}')
                                            verifyImage = False
                                            break
                                if verifyImage:
                                    continue
                            mk_path = os.path.join(tmpdir, "docs", base_name + '.md')
                            mk_data = open(mk_path).read()
                            matches = re.findall(pattern, mk_data)
                            images = []
                            for match in matches:
                                if 'static001.geekbang.org' not in match:
                                    continue
                                match = match if match.count(')') <= 0 else match[:match.index(')')]
                                if match.count('('):
                                    match = match[match.index('(') + 1:]
                                images.append(match)
                            with ThreadPoolExecutor(max_workers=3) as executor:
                                futures = [executor.submit(http_get_base64, img_url, timeout) for img_url in images]
                                for future in futures:
                                    bs, im_uri = future.result()
                                    if bs and im_uri:
                                        print(im_uri.split(".")[1])
                                        mk_data = mk_data.replace(im_uri, f'data:image/png;base64,{bs}')
                                        print('replace image', im_uri, mk_path)

                            with open(mk_path, "w") as wm:
                                wm.write(mk_data)

                        proc = subprocess.Popen(
                            ["mkdocs", "serve", "--no-livereload", "-a", f"127.0.0.1:{port}"],
                                 cwd=tmpdir,  stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


                        pdfs = []
                        for nav in data.get('nav'):
                            if not isinstance(nav, str):
                                raise ValueError(dirname + nav)
                            base_name = os.path.splitext(nav)[0]
                            target = os.path.join(part_dir, base_name.replace("%", "")+".pdf")
                            uri = host if base_name == "index" else host + html.escape(base_name)

                            if os.path.exists(target) and round(os.path.getsize(target)/1024, 2) > 10:
                                verifyImage = True
                                for page in PdfReader(target).pages:
                                    if not verifyImage:
                                        break
                                    for img in page.images:
                                        if img.image.size == (28, 32):
                                            print(f'image not verify: {target}')
                                            verifyImage = False
                                            break
                                if verifyImage:
                                    mk_path = os.path.join(tmpdir, "docs", base_name + '.md')
                                    mk_data = open(mk_path).read()
                                    pdfs.append((target, base_name, mk_data))
                                    continue

                            result = worker(driver, uri, timeout)
                            if compress:
                                __compress(result, target, power)
                                print(f"__compress {target}")
                            else:
                                with open(target, "wb") as file:
                                    file.write(result)
                                    print(f"writing {target}")
                            pdfs.append((target, base_name, mk_data))


                        proc.kill()
                        os.popen("lsof -i:" + str(port) + " | grep -v 'PID' | awk '{print $2}' |  xargs kill -9")

                        output_dir = f'{output}/{os.path.basename(os.path.dirname(dirname))}'
                        if not os.path.exists(output_dir):
                            os.makedirs(output_dir, exist_ok=True)

                        merger_pdfs = []
                        if len(pdfs) < 200:
                            pdf_name = f"{os.path.basename(dirname)}.pdf"
                            pdf_fpath = os.path.join(dirname, pdf_name)
                            output_file = os.path.join(output_dir, pdf_name)
                            merger_pdfs.append((pdf_fpath, output_file, pdfs))
                        else:
                            pdf_name = f"{os.path.basename(dirname)}-上.pdf"
                            pdf_fpath = os.path.join(dirname, pdf_name)
                            output_file = os.path.join(output_dir, pdf_name)
                            merger_pdfs.append((pdf_fpath, output_file, pdfs[0:100]))
                            pdf_name = f"{os.path.basename(dirname)}-下.pdf"
                            pdf_fpath = os.path.join(dirname, pdf_name)
                            output_file = os.path.join(output_dir, pdf_name)
                            merger_pdfs.append((pdf_fpath, output_file, pdfs[100:]))

                        for pdf_path, output_path, merger_pdf in merger_pdfs:
                            merger = PdfWriter()
                            for (pdf, name, text) in merger_pdf:
                                merger.append(pdf)

                            merger.write(pdf_path)
                            print(f"writing pdf {pdf_path}")
                            merger.close()

                            os.rename(pdf_path, output_path)
                            with PdfWriter() as writer:
                                with open(output_path, "rb") as fd:
                                    writer.append(fd)
                                    count = 0
                                    for (pdf, name, text) in merger_pdf:
                                        with PdfReader(pdf) as reader:
                                            page = reader.get_num_pages()
                                            writer.add_outline_item(title=name, page_number=count, parent=None)
                                            count += page
                                    writer.write(output_path)
                                    print(f"writing pdf {output_path}")
                        break
                except Exception as e:
                    print(f"exception: {e}, traceback: {traceback.format_exc()}")
                    if 'No such file or directory' in str(e):
                        driver.quit()
                        os.popen("lsof -i:" + str(port) + " | grep -v 'PID' | awk '{print $2}' |  xargs kill -9")
                        break
                finally:
                    driver.quit()


@click.command("pdf")
@click.option(
    "-i",
    "--source",
    required=True,
    help="source is path",
)
@click.option(
    "-o",
    "--output",
    default=os.getcwd(),
    help="output is dir",
)
@click.option(
    "-t",
    "--timeout",
    type=int,
    default=9,
    help="get url with browser timeout",
)
@click.option(
    "-c",
    "--compress",
    type=bool,
    default=False,
    help="PDF is compressed or not. Default value is False",
)
@click.option(
    "-p",
    "--power",
    type=int,
    default=0,
    help="power of the compression. Default value is 0. This can be 0: default, 1: prepress, 2: printer, 3: ebook, 4: screen",
)
@click.option(
    "-a",
    "--port",
    type=int,
    default=8000,
    help="mkdocs port. Default value is 8000",
)
def make_pdf(source, output, timeout, compress, power, port):
    webdriver_options = Options()
    webdriver_prefs = {
        'profile.default_content_setting_values': {
            'notifications': 2
        }
    }
    webdriver_options.add_argument("--headless")
    webdriver_options.add_argument("--disable-gpu")
    webdriver_options.add_argument("--no-sandbox")
    webdriver_options.add_argument("--disable-dev-shm-usage")
    webdriver_options.experimental_options["prefs"] = webdriver_prefs

    http_client = requests.Session()
    http_client.proxies = {
        "http": "http://127.0.0.1:1087",
        "https": "http://127.0.0.1:1087",
    }
    download_manager = WDMDownloadManager(http_client=http_client)
    service = Service(ChromeDriverManager(download_manager=download_manager).install())
    host = f"http://127.0.0.1:{port}/"
    source = os.path.abspath(source)
    basename = os.path.basename(source)
    for i in range(9):
        os.popen("lsof -i:" + str(port) + " | grep -v 'PID' | awk '{print $2}' |  xargs kill -9")
        driver = webdriver.Chrome(service=service, options=webdriver_options)
        try:
            parts_dir = os.path.join(source, "parts")
            pattern = r'https?://[^\s]+'
            fpath = os.path.join(source, "mkdocs.yml")
            data = yaml.safe_load(open(fpath))
            print(f'basename: {basename}')
            navs = data.get('nav')
            proc = subprocess.Popen(
                ["mkdocs", "serve", "--no-livereload", "-a", f"127.0.0.1:{port}"],
                cwd=source, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

            part_dir = os.path.join(parts_dir, basename)
            if not os.path.exists(part_dir):
                os.makedirs(part_dir, exist_ok=True)

            pdfs = []
            for nav in navs:
                if not isinstance(nav, str):
                    raise ValueError(source + nav)
                base_name = os.path.splitext(nav)[0]
                target = os.path.join(part_dir, base_name.replace("%", "") + ".pdf")
                uri = host if base_name == "index" else host + html.escape(base_name)
                mk_path = os.path.join(source, "docs", base_name + '.md')
                mk_data = open(mk_path).read()
                matches = re.findall(pattern, mk_data)
                images = []
                for match in matches:
                    if 'static001.geekbang.org' not in match:
                        continue
                    match = match if match.count(')') <= 0 else match[:match.index(')')]
                    if match.count('('):
                        match = match[match.index('(') + 1:]
                    images.append(match)

                if os.path.exists(target) and round(os.path.getsize(target) / 1024, 2) > 10:
                    verifyImage = True
                    for page in PdfReader(target).pages:
                        if not verifyImage:
                            break
                        for img in page.images:
                            if img.image.size == (28, 32):
                                print(f'image not verify: {target}')
                                verifyImage = False
                                break
                    if verifyImage:
                        pdfs.append((target, base_name, mk_data, images))
                        continue

                with ThreadPoolExecutor(max_workers=3) as executor:
                    [executor.submit(http_head, img_url, timeout) for img_url in images]

                result = worker(driver, uri, timeout)
                if compress:
                    __compress(result, target, power)
                    print(f"__compress {target}")
                else:
                    with open(target, "wb") as file:
                        file.write(result)
                        print(f"writing {target}")
                pdfs.append((target, base_name, mk_data, images))

            proc.kill()
            os.popen("lsof -i:" + str(port) + " | grep -v 'PID' | awk '{print $2}' |  xargs kill -9")
            merger = PdfWriter()
            for (pdf, name, text, images) in pdfs:
                merger.append(pdf)
            pdf_name = f"{os.path.basename(source)}.pdf"
            pdf_path = os.path.join(source, pdf_name)
            merger.write(pdf_path)
            print(f"writing pdf {pdf_path}")
            merger.close()
            output_path = f'{output}/{os.path.basename(os.path.dirname(source))}/{pdf_name}'
            if not os.path.exists(os.path.dirname(output_path)):
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
            print(output_path)
            os.rename(pdf_path, output_path)
            with PdfWriter() as writer:
                with open(output_path, "rb") as fd:
                    writer.append(fd)
                    count = 0
                    for (pdf, name, text, images) in pdfs:
                        with PdfReader(pdf) as reader:
                            page = reader.get_num_pages()
                            writer.add_outline_item(title=name, page_number=count, parent=None)
                            count += page
                    writer.write(output_path)
                    print(f"writing pdf {output_path}")
            break
        except Exception as e:
            print(f"exception: {e}, traceback: {traceback.format_exc()}")
            if 'No such file or directory' in str(e):
                driver.quit()
                os.popen("lsof -i:" + str(port) + " | grep -v 'PID' | awk '{print $2}' |  xargs kill -9")
                break
        finally:
            driver.quit()



@click.group(invoke_without_command=True)
@click.pass_context
def heya(ctx):
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())

heya.add_command(make_pdf)
heya.add_command(make_all_pdf)
def main() -> int:
    return heya(auto_envvar_prefix="HEYA")

if __name__ == '__main__':
    sys.exit(main())