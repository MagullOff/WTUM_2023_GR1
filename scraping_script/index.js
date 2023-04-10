const puppeteer = require("puppeteer");
const fs = require("fs");

const teamAbbreviations = {
  "Atlanta Hawks": "ATL",
  "Boston Celtics": "BOS",
  "Brooklyn Nets": "BKN",
  "Charlotte Hornets": "CHA",
  "Chicago Bulls": "CHI",
  "Cleveland Cavaliers": "CLE",
  "Dallas Mavericks": "DAL",
  "Denver Nuggets": "DEN",
  "Detroit Pistons": "DET",
  "Golden State Warriors": "GSW",
  "Houston Rockets": "HOU",
  "Indiana Pacers": "IND",
  "Los Angeles Clippers": "LAC",
  "Los Angeles Lakers": "LAL",
  "Memphis Grizzlies": "MEM",
  "Miami Heat": "MIA",
  "Milwaukee Bucks": "MIL",
  "Minnesota Timberwolves": "MIN",
  "New Orleans Pelicans": "NOP",
  "New York Knicks": "NYK",
  "Oklahoma City Thunder": "OKC",
  "Orlando Magic": "ORL",
  "Philadelphia 76ers": "PHI",
  "Phoenix Suns": "PHX",
  "Portland Trail Blazers": "POR",
  "Sacramento Kings": "SAC",
  "San Antonio Spurs": "SAS",
  "Toronto Raptors": "TOR",
  "Utah Jazz": "UTA",
  "Washington Wizards": "WAS",
};

(async () => {
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();

  await page.goto("https://www.flashscore.pl/koszykowka/usa/nba/mecze/");

  console.log("Fetching available matches...");
  const matches = await page.$$(".event__match");

  const matchIds = (
    await Promise.all(
      matches.map(
        async (matchHandle) =>
          await page.evaluate((matchHandle) => matchHandle.id, matchHandle)
      )
    )
  ).map((id) => id.slice(4));

  console.log(`Fetching succeeded with ${matchIds.length} results`);

  const matchData = await Promise.all(
    matchIds.map(async (id) => {
      const matchPage = await browser.newPage();
      await matchPage.goto(
        `https://www.flashscore.pl/mecz/${id}/#/szczegoly-meczu`
      );

      const dateElement = await matchPage.$(
        ".duelParticipant__startTime > div"
      );
      const date = await matchPage.evaluate(
        (dateElement) => dateElement.textContent,
        dateElement
      );

      const teamElements = await matchPage.$$(
        ".participant__participantName .participant__overflow"
      );
      const teamNames = {
        home: teamAbbreviations[
          await matchPage.evaluate(
            (teamElement) => teamElement.textContent,
            teamElements[0]
          )
        ],
        away: teamAbbreviations[
          await matchPage.evaluate(
            (teamElement) => teamElement.textContent,
            teamElements[1]
          )
        ],
      };

      const oddsElements = await matchPage.$$(".oddsValueInner");
      const odds = {
        home: await matchPage.evaluate(
          (oddsElements) => oddsElements.textContent,
          oddsElements[0]
        ),
        away: await matchPage.evaluate(
          (oddsElements) => oddsElements.textContent,
          oddsElements[1]
        ),
      };

      return { date, teamNames, odds };
    })
  );

  await browser.close();

  let fileContent = "team_home,team_away,Win,Loss,Date\n";

  matchData.forEach((data) => {
    fileContent += `${data.teamNames.home},${data.teamNames.away},${data.odds.home},${data.odds.away},${data.date}\n`;
  });

  fs.writeFile("data.txt", fileContent, (err) => {
    if (err) {
      console.log(err);
    }
    console.log("Data written to data.txt. Script completed successfully!");
  });
})();
