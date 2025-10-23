"""Web scrapers for football data sources"""

import logging
import time
from typing import Dict, List, Optional
from abc import ABC, abstractmethod
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Base class for web scrapers"""

    def __init__(self, timeout: int = 15):
        self.timeout = timeout
        self.user_agent = (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/120.0.0.0 Safari/537.36'
        )

    @abstractmethod
    def _get_base_url(self) -> str:
        """Get base URL for scraping"""
        pass

    def _get_driver(self, headless: bool = True) -> webdriver.Chrome:
        """
        Create Chrome WebDriver instance

        Args:
            headless: Run in headless mode

        Returns:
            Chrome WebDriver
        """
        chrome_options = Options()

        if headless:
            chrome_options.add_argument('--headless')

        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument(f'user-agent={self.user_agent}')

        try:
            driver = webdriver.Chrome(options=chrome_options)
            driver.set_page_load_timeout(self.timeout)
            return driver
        except WebDriverException as e:
            logger.error(f"Failed to create WebDriver: {e}")
            raise

    def _get_soup(self, url: str) -> BeautifulSoup:
        """
        Get BeautifulSoup object for URL

        Args:
            url: URL to scrape

        Returns:
            BeautifulSoup object
        """
        headers = {'User-Agent': self.user_agent}

        try:
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            logger.error(f"Failed to fetch URL {url}: {e}")
            raise


class UnderstatScraper(BaseScraper):
    """Scraper for Understat.com (xG data)"""

    def _get_base_url(self) -> str:
        return "https://understat.com"

    def scrape_team_xg(self, team_name: str, season: str = "2024") -> Optional[Dict]:
        """
        Scrape team xG data

        Args:
            team_name: Team name (e.g., 'Barcelona', 'Liverpool')
            season: Season year

        Returns:
            Dict with xG and xGA or None if failed
        """
        driver = None

        try:
            # Normalize team name for URL
            team_slug = team_name.replace(' ', '_')
            url = f"{self._get_base_url()}/team/{team_slug}/{season}"

            driver = self._get_driver()
            driver.get(url)

            # Wait for JavaScript to load
            wait = WebDriverWait(driver, 10)
            wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "progress-bar"))
            )

            # Extract xG data
            xg_elements = driver.find_elements(By.CSS_SELECTOR, ".progress-bar span")

            if len(xg_elements) >= 2:
                xg = float(xg_elements[0].text)
                xga = float(xg_elements[1].text)

                return {
                    "xG": xg,
                    "xGA": xga,
                    "source": "understat",
                    "scraped_at": datetime.now().isoformat()
                }

            return None

        except (TimeoutException, WebDriverException, ValueError) as e:
            logger.error(f"Understat scraping failed for {team_name}: {e}")
            return None

        finally:
            if driver:
                driver.quit()

    def scrape_match_xg(self, match_id: str) -> Optional[Dict]:
        """
        Scrape match xG data

        Args:
            match_id: Understat match ID

        Returns:
            Dict with match xG data or None
        """
        driver = None

        try:
            url = f"{self._get_base_url()}/match/{match_id}"

            driver = self._get_driver()
            driver.get(url)

            # Wait for data
            wait = WebDriverWait(driver, 10)
            wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "scheme-block"))
            )

            # Extract xG values from page
            xg_home = driver.find_element(
                By.CSS_SELECTOR,
                ".progress-bar:nth-child(1) span"
            ).text
            xg_away = driver.find_element(
                By.CSS_SELECTOR,
                ".progress-bar:nth-child(2) span"
            ).text

            return {
                "xG_home": float(xg_home),
                "xG_away": float(xg_away),
                "source": "understat",
                "match_id": match_id,
                "scraped_at": datetime.now().isoformat()
            }

        except (TimeoutException, WebDriverException, ValueError) as e:
            logger.error(f"Understat match scraping failed for {match_id}: {e}")
            return None

        finally:
            if driver:
                driver.quit()


class FBrefScraper(BaseScraper):
    """Scraper for FBref.com (advanced stats)"""

    def _get_base_url(self) -> str:
        return "https://fbref.com"

    def scrape_team_stats(self, squad_id: str, season: str = "2024-2025") -> Optional[Dict]:
        """
        Scrape team advanced statistics

        Args:
            squad_id: FBref squad ID
            season: Season string (e.g., '2024-2025')

        Returns:
            Dict with advanced stats or None
        """
        try:
            url = f"{self._get_base_url()}/en/squads/{squad_id}/{season}/all_comps"

            # Read HTML tables with pandas
            tables = pd.read_html(url)

            stats = {
                "source": "fbref",
                "squad_id": squad_id,
                "season": season,
                "scraped_at": datetime.now().isoformat()
            }

            # Extract relevant statistics from tables
            for table in tables:
                # Identify table by columns
                columns = [str(col).lower() for col in table.columns]

                # Shooting stats
                if any('shot' in col for col in columns):
                    if 'Gls' in table.columns and 'Sh' in table.columns:
                        stats['goals'] = table['Gls'].sum()
                        stats['shots'] = table['Sh'].sum()
                        if 'SoT' in table.columns:
                            stats['shots_on_target'] = table['SoT'].sum()

                # Passing stats
                if 'cmp' in ' '.join(columns):
                    if 'Cmp' in table.columns and 'Att' in table.columns:
                        stats['passes_completed'] = table['Cmp'].sum()
                        stats['passes_attempted'] = table['Att'].sum()
                        if 'Cmp%' in table.columns:
                            stats['pass_completion_pct'] = table['Cmp%'].mean()

                # Defensive stats
                if 'tackle' in ' '.join(columns):
                    if 'Tkl' in table.columns:
                        stats['tackles'] = table['Tkl'].sum()
                    if 'Int' in table.columns:
                        stats['interceptions'] = table['Int'].sum()

            return stats if len(stats) > 4 else None

        except Exception as e:
            logger.error(f"FBref scraping failed for {squad_id}: {e}")
            return None

    def scrape_match_report(self, match_id: str) -> Optional[Dict]:
        """
        Scrape match report

        Args:
            match_id: FBref match ID

        Returns:
            Dict with match statistics or None
        """
        try:
            url = f"{self._get_base_url()}/en/matches/{match_id}"

            soup = self._get_soup(url)

            # Extract basic match info
            match_info = soup.find('div', class_='scorebox')

            if not match_info:
                return None

            stats = {
                "source": "fbref",
                "match_id": match_id,
                "scraped_at": datetime.now().isoformat()
            }

            # Try to read statistics tables
            try:
                tables = pd.read_html(url)
                if tables:
                    stats['tables_found'] = len(tables)
            except Exception:
                pass

            return stats

        except Exception as e:
            logger.error(f"FBref match report scraping failed for {match_id}: {e}")
            return None


class TransfermarktScraper(BaseScraper):
    """Scraper for Transfermarkt.com (injuries, market values)"""

    def _get_base_url(self) -> str:
        return "https://www.transfermarkt.com"

    def scrape_team_injuries(self, team_id: int, team_slug: str) -> List[Dict]:
        """
        Scrape team injury list

        Args:
            team_id: Transfermarkt team ID
            team_slug: Team URL slug

        Returns:
            List of injury dicts
        """
        try:
            url = f"{self._get_base_url()}/{team_slug}/verletzungen/verein/{team_id}"

            soup = self._get_soup(url)

            injuries = []
            injury_table = soup.find('table', class_='items')

            if not injury_table:
                logger.warning(f"No injury table found for team {team_id}")
                return injuries

            rows = injury_table.find('tbody').find_all('tr')

            for row in rows:
                try:
                    cells = row.find_all('td')

                    if len(cells) < 6:
                        continue

                    # Extract player info
                    player_elem = cells[0].find('a', class_='spielprofil_tooltip')
                    if not player_elem:
                        continue

                    player_name = player_elem.text.strip()
                    player_id = player_elem.get('id', '').replace('player_', '')

                    # Injury info
                    injury_type = cells[3].text.strip() if len(cells) > 3 else "Unknown"
                    return_date = cells[5].text.strip() if len(cells) > 5 else None

                    injuries.append({
                        "player_id": player_id,
                        "player_name": player_name,
                        "injury_type": injury_type,
                        "expected_return": return_date,
                        "source": "transfermarkt",
                        "scraped_at": datetime.now().isoformat()
                    })

                except Exception as e:
                    logger.warning(f"Failed to parse injury row: {e}")
                    continue

            return injuries

        except Exception as e:
            logger.error(f"Transfermarkt injuries scraping failed for team {team_id}: {e}")
            return []

    def scrape_squad_value(self, team_id: int, team_slug: str) -> Optional[Dict]:
        """
        Scrape squad market value

        Args:
            team_id: Transfermarkt team ID
            team_slug: Team URL slug

        Returns:
            Dict with market value data or None
        """
        try:
            url = f"{self._get_base_url()}/{team_slug}/startseite/verein/{team_id}"

            soup = self._get_soup(url)

            # Find squad value element
            value_elem = soup.find('a', class_='data-header__market-value-wrapper')

            if value_elem:
                value_text = value_elem.text.strip()

                return {
                    "squad_value_text": value_text,
                    "source": "transfermarkt",
                    "team_id": team_id,
                    "scraped_at": datetime.now().isoformat()
                }

            return None

        except Exception as e:
            logger.error(f"Transfermarkt value scraping failed for team {team_id}: {e}")
            return None


# Factory function
def get_scraper(scraper_type: str) -> BaseScraper:
    """
    Get scraper by type

    Args:
        scraper_type: 'understat', 'fbref', or 'transfermarkt'

    Returns:
        Scraper instance
    """
    scrapers = {
        'understat': UnderstatScraper,
        'fbref': FBrefScraper,
        'transfermarkt': TransfermarktScraper,
    }

    scraper_class = scrapers.get(scraper_type.lower())
    if not scraper_class:
        raise ValueError(f"Unknown scraper type: {scraper_type}")

    return scraper_class()
