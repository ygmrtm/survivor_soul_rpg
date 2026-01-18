# Survivor Soul RPG Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2024-11-13
### Added
- Initial release of Survivor Soul RPG.
- Flask microservices architecture with endpoints for Notion and Todoist integrations.
- Landing page with Lovecraftian theme displaying character cards in a grid.
- Basic structure for the following endpoints:
  - **Notion API**: `getAllCharacters`, `updateCharacter`, `filterByDeepLevel`
  - **Adventure Core**: `createAdventure`, `executeAdventure`, `createChallenge`, `getChallengesByDateRange`
  - **Todoist API**: `createTodoistTask`
- Integration with **Notion API** for character data.
- Integration with **Todoist SDK** for creating daily tasks and challenges.
- Error handling with custom 404 and 500 error pages.
- Global logging system with log levels (`debug`, `info`, `warn`, `error`).
- Docker-based deployment configuration.
- CI/CD setup with GitHub Actions for automated testing and deployment.
- Comprehensive README with project overview, setup instructions, and usage details.

### Changed
- N/A

### Removed
- N/A
---
## [1.0.1] - 2024-12-03
- Merge 489595feb3cfdde96c2b2246994c567f75649f45 into 2b862feb194aa5718c41237822e3d654869308de
- Update CHANGELOG for version
- Update python-app.yml
---
## [1.0.2] - 2024-12-04
- Update python-app.yml
- Update CHANGELOG for version 1.0.2
- Merge 66550d740fea0fa5b93ea5a05e77a1bc41072a8f into 14b77d30366ba02295ab2014d8a7bfc7c1f39f90
- feat: Execute Adventure 
- dummy execution
- style: CreateChallenge Button
- [x]  style: Footer w/exit
- [x]  style: CreateChallenge Button
---

## [1.0.3] - 2024-12-17
Merge cef44231c9cb5d6d86044341478260c60609bba2 into ea8e00526c7fa74aeaf98368d2077614624649bb

feat: Execute Adventure

- [x]  feat: Execute Adventure
    - [x]  system of fight
    - [x]  consider negotiate
    - [x]  reward system
    - [x]  Logging in paragraphs

Update CHANGELOG for version 1.0.2

Update python-app.yml
Update CHANGELOG for version 1.0.2
---

## [1.0.4] - 2024-12-17
Merge aa220b3811c1d1fa13082bea65d9126a7f29847c into 873f008d14a1466a14f07bfe214dc102f800689b

Merge pull request #8 from ygmrtm/feat_underworld

[CODE-41] Feat underworld
feat: Tribute System for Challenges

Merge pull request #7 from ygmrtm/fix_ui-do-not-refresh-the-next-adventure

[CODE-41] Fix UI do not refresh the next adventure
fix: After executing an Adventure, the UI do not refresh the next Adventure

- [x]  fix: [Issue](https://github.com/ygmrtm/survivor_soul_rpg/issues/3)
---

## [1.0.5] - 2024-12-26
Merge 8d57e1c19bb4b016525347b686d1e79bf1a2a022 into 34f6001bf25e15dc4a87364a1cef11fbd678d528

feat: afterlife’s Adventure

fix: respawn

fix: adventure log

Merge pull request #13 from ygmrtm/feat_executeChagenge

[CODE-41] Feat execute challenge to underworld
---

## [1.0.6] - 2024-12-26
Merge d029ed4e561023195e73d6b8e0d226ef659a9368 into cca74683e33f612eeb9ccaa2d78d20d6ecbae955

Update CHANGELOG for version 1.0.5

Merge 8d57e1c19bb4b016525347b686d1e79bf1a2a022 into 34f6001bf25e15dc4a87364a1cef11fbd678d528

feat: afterlife’s Adventure (punishment)

- [x]  feat: afterlife’s Adventure
    - [x]  Create **Underworld Training 101** for *deadpeople*
    - [x]  Execute **101**
    - [x]  Resting/Dying Characters
    - [x]  Enable Punishment

feat: afterlife’s Adventure
---

## [1.0.7] - 2025-01-03
Merge branch 'feat_abilities' into main
Merge pull request #18 from ygmrtm/feat_stencilintegration

[CODE-41] Feat stencilintegration to abilities branch
Merge pull request #17 from ygmrtm/feat_bikeIntegration

[CODE-41] Feat bike integration to abilities branch
Merge pull request #16 from ygmrtm/feat_codingIntegration

[CODE-41] Feat coding integration merge to abilities branch
feat: Integration with **Stencil**

- [ ]  feat:Update abilities (like habits)
    - [x]  Integration with **Code**
    - [x]  Integration with **Stencil**
    - [x]  Integration with **Bike**
    - [ ]  Integration with **Epics**
    - [x]  Consider not punishment if status Stand-by
---

## [1.0.8] - 2025-01-08
Merge 7f79ba6e9aa3b591e1018627e63319af87922e93 into e9a9ac621f4c27f6cbb7b4b3efb68a438d19ad73

feat: won past challenges

- [x]  feat: Execute Challenge
    - [x]  Old **Challenges**
        - [x]  expired
        - [x]  won
            - [x]  Integration with dlychcklst
        - [x]  missed

Merge pull request #20 from ygmrtm/feat_epics

[CODE-41] Integration with **Epics** to Abilities branch
Integration with **Epics**

- [x]  feat:Update abilities (like habits)
    - [x]  Integration with **Code**
    - [x]  Integration with **Stencil**
    - [x]  Integration with **Bike**
    - [x]  Integration with **Epics**
    - [x]  Consider not punishment if status Stand-by

Merge pull request #19 from ygmrtm/main

[CODE-41] main branch to abilities
---

## [1.0.9] - 2025-01-08
Merge fa087d45b486cc3444c62a8a86f78fdb63cb6c68 into 539912a9459e30c23cc0a336ab4751d80f8db9c2

Issue with start and end dates by week

[Week 1 start and end dates is not accurate](https://github.com/ygmrtm/survivor_soul_rpg/issues/23)

Update CHANGELOG for version 1.0.8

Merge 7f79ba6e9aa3b591e1018627e63319af87922e93 into e9a9ac621f4c27f6cbb7b4b3efb68a438d19ad73

feat: won past challenges

- [x]  feat: Execute Challenge
    - [x]  Old **Challenges**
        - [x]  expired
        - [x]  won
            - [x]  Integration with dlychcklst
        - [x]  missed
---

## [1.0.10] - 2025-01-08
Merge d122995c49c74b5cf402e557572b78b272eae6a5 into 1f29470eed9857c85c68e671928cfd17d51d2c2b

Merge pull request #26 from ygmrtm/feat_whatthefucktodo_wonchallenges_adventures

[CODE-41 ] feat: won past challenges
Merge pull request #22 from ygmrtm/feal_dlylog_abilities

[CODE-41] Feat: dlylog abilities
Update CHANGELOG for version 1.0.9

Merge fa087d45b486cc3444c62a8a86f78fdb63cb6c68 into 539912a9459e30c23cc0a336ab4751d80f8db9c2
---

## [1.1.11] - 2025-01-11
Merge 0b349afceb64821d6ff62daf6ed0949812bfabaf into 378d165bc09874bc62cc0873d8986590b9c425fe

Caching Characters release

- [x]  **enhance:** *Caching* Characters by key
    - [x]  Integration with redis
    - [x]  by DeepLevel
    - [x]  By ID
    - [x]  feat: Flush Cache

**enhance:** *Caching* Characters by key

- [x]  **enhance:** *Caching* Characters by key
    - [x]  Integration with redis
    - [x]  by DeepLevel
    - [x]  By ID

Integration with redis first draft

- [ ]  **enhance:** *Caching* Characters by key
    - [x]  Integration with redis

Update CHANGELOG for version 1.0.10
---

## [1.1.12] - 2025-01-21
Merge 4bf943a3c99e8896e8bccff3f8c03e00a01821c9 into b9c83947c14d6ba28629b599ce80aa874a79e6cd

Merge pull request #35 from ygmrtm/enhace_abilities_habits_caching

[CODE-41] Enhace abilities habits caching
Feat: Evaluate and Close BreakStreak challenges.

- [x]  **enhance:** Habits and Abilities cache
    - [x]  Habits and Abilities cache
    - [x]  Top Racha by habits *w Todoist*
    - [x]  Create challenge to break last Racha
    - [x]  Evaluate and Close BreakStreak challenges.

feat: Create challenge to break last Racha

adding cache for deadpeople
---

## [1.1.13] - 2025-01-24
Merge c25c4b65d6129f14f99103db35cfba2b9229de58 into 75d983282604faa6301f43cd7ee38d950ee61fc7

Merge pull request #39 from ygmrtm/feat_tournaments

[Code-41] Feat tournaments
feat: Tournament | All(joining forces)(use difficult level = amount of teammates) vs Root+6Bosses

Merge pull request #37 from ygmrtm/main

[CODE-41] Udating Tournament branch
Update CHANGELOG for version 1.1.12
---

## [1.1.14] - 2025-04-18
Merge c2b0cf16476b960187bf0744b6e74a278e775871 into 0f19c228831c3780284d8a2dd85323ea51bd6c3b

Merge pull request #43 from ygmrtm/42-in-the-weekly-challenges-create_habit_longest_streak-is-getting-zeroes

[CODE-41] Fix to handle cursor in DailyChecklist
Fix to handle cursor in DailyChecklist

**enhance:** cards displayed/enabled also consider **status** *(not only hp)*

- [x]  **enhance:** cards displayed/enabled also consider **status** *(not only hp)*
    - [x]  color of the displayed status

enhacements

- Include Racha from Redis
- Underworld values
- Tournament minor changes
---

## [1.1.15] - 2025-04-18
Merge d8624da4bdbf69f4389150299ca640794a29a2bb into 3f9052bda4a3e8cfeaa0331e3bb6a60f1c78b123

Merge branch 'enhacements' of https://github.com/ygmrtm/survivor_soul_rpg into enhacements

Code Change for Undead

Merge pull request #45 from ygmrtm/main

[CODE-41] Refresh
Update CHANGELOG for version 1.1.14
---

## [1.1.16] - 2025-05-06
Merge 2b48bbc0e25bbb51b87c289b9ef22bf6edf2c670 into 1129f0008449528ba3138a04e145b7cbaee0c3d5

fix: was too much implemented on matches

was too much

Update CHANGELOG for version 1.1.15

Merge d8624da4bdbf69f4389150299ca640794a29a2bb into 3f9052bda4a3e8cfeaa0331e3bb6a60f1c78b123

Merge branch 'enhacements' of https://github.com/ygmrtm/survivor_soul_rpg into enhacements
---

## [1.2.1] - 2025-05-14
Merge fc6db2581e594ad347e6faf8eea50e03f0a78761 into 65f290a327b550918f63670dcd58fe2a025237c2

feature: flush button

feature: Pill | Health

first draft, running only displaying. functionality pending

FIX tournament

Merge pull request #48 from ygmrtm/main

[CODE-41] upd
---

## [1.2.2] - 2025-05-21
Merge 201278340d10503dd47e7d283ad0a4e542747b15 into 3dd05a137a02683e198a578e8c3b3e2100cfe1d9

enhance: Underworld result in logging

FIX: Gods with kids need to reborn fast

- [x]  **feature:** capsule pill health color (full button)
- [x]  **fix:** if the Gods with kids goes death, then what?

feature: capsule pill health color (full button)

- [x]  **feature:** capsule pill health color (full button)
    - [ ]  **feature:** capsule pill by survivor card

feature: pills | initial flow counting 'em
---

## [1.2.3] - 2025-11-22
Merge 7b0b8f85e7d50a8e8bec063b2abaebc4eb92cdcf into 9904f2310b8491bacfa1e6ff35a0ba35dfd61c23

minor change

mayor changes

- [ ]  Add movies to Habits counts and statistics.
- [ ]  Add the 366, 182, 91 and 31 days for Habits Streaks
- [ ]  Add the current streak to the current:
**GYM| longest:*3 days*| nextSuggested:*5 days*
current: ## |** daysSince:*11 days* | last time checked on **2025-05-12**
- [ ]  Reactivate Pills button/cache after *Deadventures.*

Adding pills missing

feature: first draft of ticktick integration

no functional yet but it will take a few days
---

## [1.3.1] - 2025-12-16
Merge b44e3614bda0f267dbd4ba3ce446fcfbd8bddac4 into eea729096ac9a1fe19da1594c9631eaf5cd9da27

Done version with watchlist included

First version for Individual Challenges invocations

missing testing

Watchlist version. missing scheduled invocations

handling watchlist in cache
---

## [1.4.1] - 2025-12-16
Merge 826a5b9a4bb963c3e109ea1c1e8a8fb0cf984624 into 3cfad1fd4b94e61c853aa7be84f384622538bbeb

done witout ticktick and storing in redis

this version is implemented...

with ticktick-pl but it still sucks, cause loging was not possible.

Merge pull request #57 from ygmrtm/main

upodate ticktick branch
Update CHANGELOG for version 1.3.1
---

## [1.4.2] - 2026-01-12
Merge 313a075e90ef2170b0d2a7715595dae25d1ef921 into 85d8cd324c1b1b6bfd502e5be9f214826c70767a

Fix for watchlist

Sanitize Rich Text

requirements

Update Adventure
---

## [1.4.3] - 2026-01-18
Merge 0028315b00a787e8a30a9cc5bf4c394b8c9be043 into c4f7dedf0e1b08446e4fcabed8f30b865f737afc

Split the underworld executions

## mvp05
- [x]  Split the underworld executions and coordinate between front/back end invocations for:
    - Underworld adventures Created
    - Underworld adventures Executed
    - Underworld awaking characters
    - Adventures Punishment Execution

Update CHANGELOG for version 1.4.2

Merge 313a075e90ef2170b0d2a7715595dae25d1ef921 into 85d8cd324c1b1b6bfd502e5be9f214826c70767a

Fix for watchlist
---

