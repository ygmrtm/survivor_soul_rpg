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

