import stackexchange
class __SEAPI(str):
    def __call__(self):
        return stackexchange.Site(self)
StackOverflow = __SEAPI('stackoverflow.com')
ServerFault = __SEAPI('serverfault.com')
SuperUser = __SEAPI('superuser.com')
MetaStackExchange = __SEAPI('meta.stackexchange.com')
WebApplications = __SEAPI('webapps.stackexchange.com')
WebApplicationsMeta = __SEAPI('meta.webapps.stackexchange.com')
Arqade = __SEAPI('gaming.stackexchange.com')
ArqadeMeta = __SEAPI('meta.gaming.stackexchange.com')
Webmasters = __SEAPI('webmasters.stackexchange.com')
WebmastersMeta = __SEAPI('meta.webmasters.stackexchange.com')
SeasonedAdvice = __SEAPI('cooking.stackexchange.com')
SeasonedAdviceMeta = __SEAPI('meta.cooking.stackexchange.com')
GameDevelopment = __SEAPI('gamedev.stackexchange.com')
GameDevelopmentMeta = __SEAPI('meta.gamedev.stackexchange.com')
Photography = __SEAPI('photo.stackexchange.com')
PhotographyMeta = __SEAPI('meta.photo.stackexchange.com')
CrossValidated = __SEAPI('stats.stackexchange.com')
CrossValidatedMeta = __SEAPI('meta.stats.stackexchange.com')
Mathematics = __SEAPI('math.stackexchange.com')
MathematicsMeta = __SEAPI('meta.math.stackexchange.com')
HomeImprovement = __SEAPI('diy.stackexchange.com')
HomeImprovementMeta = __SEAPI('meta.diy.stackexchange.com')
MetaSuperUser = __SEAPI('meta.superuser.com')
MetaServerFault = __SEAPI('meta.serverfault.com')
GeographicInformationSystems = __SEAPI('gis.stackexchange.com')
GeographicInformationSystemsMeta = __SEAPI('meta.gis.stackexchange.com')
TeXLaTeX = __SEAPI('tex.stackexchange.com')
TeXLaTeXMeta = __SEAPI('meta.tex.stackexchange.com')
AskUbuntu = __SEAPI('askubuntu.com')
AskUbuntuMeta = __SEAPI('meta.askubuntu.com')
PersonalFinanceampMoney = __SEAPI('money.stackexchange.com')
PersonalFinanceampMoneyMeta = __SEAPI('meta.money.stackexchange.com')
EnglishLanguageampUsage = __SEAPI('english.stackexchange.com')
EnglishLanguageampUsageMeta = __SEAPI('meta.english.stackexchange.com')
StackApps = __SEAPI('stackapps.com')
UserExperience = __SEAPI('ux.stackexchange.com')
UserExperienceMeta = __SEAPI('meta.ux.stackexchange.com')
UnixampLinux = __SEAPI('unix.stackexchange.com')
UnixampLinuxMeta = __SEAPI('meta.unix.stackexchange.com')
WordPressDevelopment = __SEAPI('wordpress.stackexchange.com')
WordPressDevelopmentMeta = __SEAPI('meta.wordpress.stackexchange.com')
TheoreticalComputerScience = __SEAPI('cstheory.stackexchange.com')
TheoreticalComputerScienceMeta = __SEAPI('meta.cstheory.stackexchange.com')
AskDifferent = __SEAPI('apple.stackexchange.com')
AskDifferentMeta = __SEAPI('meta.apple.stackexchange.com')
RoleplayingGames = __SEAPI('rpg.stackexchange.com')
RoleplayingGamesMeta = __SEAPI('meta.rpg.stackexchange.com')
Bicycles = __SEAPI('bicycles.stackexchange.com')
BicyclesMeta = __SEAPI('meta.bicycles.stackexchange.com')
Programmers = __SEAPI('programmers.stackexchange.com')
ProgrammersMeta = __SEAPI('meta.programmers.stackexchange.com')
ElectricalEngineering = __SEAPI('electronics.stackexchange.com')
ElectricalEngineeringMeta = __SEAPI('meta.electronics.stackexchange.com')
AndroidEnthusiasts = __SEAPI('android.stackexchange.com')
AndroidEnthusiastsMeta = __SEAPI('meta.android.stackexchange.com')
BoardampCardGames = __SEAPI('boardgames.stackexchange.com')
BoardampCardGamesMeta = __SEAPI('meta.boardgames.stackexchange.com')
Physics = __SEAPI('physics.stackexchange.com')
PhysicsMeta = __SEAPI('meta.physics.stackexchange.com')
Homebrewing = __SEAPI('homebrew.stackexchange.com')
HomebrewingMeta = __SEAPI('meta.homebrew.stackexchange.com')
InformationSecurity = __SEAPI('security.stackexchange.com')
InformationSecurityMeta = __SEAPI('meta.security.stackexchange.com')
Writers = __SEAPI('writers.stackexchange.com')
WritersMeta = __SEAPI('meta.writers.stackexchange.com')
VideoProduction = __SEAPI('video.stackexchange.com')
VideoProductionMeta = __SEAPI('meta.video.stackexchange.com')
GraphicDesign = __SEAPI('graphicdesign.stackexchange.com')
GraphicDesignMeta = __SEAPI('meta.graphicdesign.stackexchange.com')
DatabaseAdministrators = __SEAPI('dba.stackexchange.com')
DatabaseAdministratorsMeta = __SEAPI('meta.dba.stackexchange.com')
ScienceFictionampFantasy = __SEAPI('scifi.stackexchange.com')
ScienceFictionampFantasyMeta = __SEAPI('meta.scifi.stackexchange.com')
CodeReview = __SEAPI('codereview.stackexchange.com')
CodeReviewMeta = __SEAPI('meta.codereview.stackexchange.com')
ProgrammingPuzzlesampCodeGolf = __SEAPI('codegolf.stackexchange.com')
ProgrammingPuzzlesampCodeGolfMeta = __SEAPI('meta.codegolf.stackexchange.com')
QuantitativeFinance = __SEAPI('quant.stackexchange.com')
QuantitativeFinanceMeta = __SEAPI('meta.quant.stackexchange.com')
ProjectManagement = __SEAPI('pm.stackexchange.com')
ProjectManagementMeta = __SEAPI('meta.pm.stackexchange.com')
Skeptics = __SEAPI('skeptics.stackexchange.com')
SkepticsMeta = __SEAPI('meta.skeptics.stackexchange.com')
PhysicalFitness = __SEAPI('fitness.stackexchange.com')
PhysicalFitnessMeta = __SEAPI('meta.fitness.stackexchange.com')
DrupalAnswers = __SEAPI('drupal.stackexchange.com')
DrupalAnswersMeta = __SEAPI('meta.drupal.stackexchange.com')
MotorVehicleMaintenanceampRepair = __SEAPI('mechanics.stackexchange.com')
MotorVehicleMaintenanceampRepairMeta = __SEAPI('meta.mechanics.stackexchange.com')
Parenting = __SEAPI('parenting.stackexchange.com')
ParentingMeta = __SEAPI('meta.parenting.stackexchange.com')
SharePoint = __SEAPI('sharepoint.stackexchange.com')
SharePointMeta = __SEAPI('meta.sharepoint.stackexchange.com')
MusicPracticeampTheory = __SEAPI('music.stackexchange.com')
MusicPracticeampTheoryMeta = __SEAPI('meta.music.stackexchange.com')
SoftwareQualityAssuranceampTesting = __SEAPI('sqa.stackexchange.com')
SoftwareQualityAssuranceampTestingMeta = __SEAPI('meta.sqa.stackexchange.com')
MiYodeya = __SEAPI('judaism.stackexchange.com')
MiYodeyaMeta = __SEAPI('meta.judaism.stackexchange.com')
GermanLanguage = __SEAPI('german.stackexchange.com')
GermanLanguageMeta = __SEAPI('meta.german.stackexchange.com')
JapaneseLanguage = __SEAPI('japanese.stackexchange.com')
JapaneseLanguageMeta = __SEAPI('meta.japanese.stackexchange.com')
Philosophy = __SEAPI('philosophy.stackexchange.com')
PhilosophyMeta = __SEAPI('meta.philosophy.stackexchange.com')
GardeningampLandscaping = __SEAPI('gardening.stackexchange.com')
GardeningampLandscapingMeta = __SEAPI('meta.gardening.stackexchange.com')
Travel = __SEAPI('travel.stackexchange.com')
TravelMeta = __SEAPI('meta.travel.stackexchange.com')
PersonalProductivity = __SEAPI('productivity.stackexchange.com')
PersonalProductivityMeta = __SEAPI('meta.productivity.stackexchange.com')
Cryptography = __SEAPI('crypto.stackexchange.com')
CryptographyMeta = __SEAPI('meta.crypto.stackexchange.com')
SignalProcessing = __SEAPI('dsp.stackexchange.com')
SignalProcessingMeta = __SEAPI('meta.dsp.stackexchange.com')
FrenchLanguage = __SEAPI('french.stackexchange.com')
FrenchLanguageMeta = __SEAPI('meta.french.stackexchange.com')
Christianity = __SEAPI('christianity.stackexchange.com')
ChristianityMeta = __SEAPI('meta.christianity.stackexchange.com')
Bitcoin = __SEAPI('bitcoin.stackexchange.com')
StackOverflow = __SEAPI('stackoverflow.com')
ServerFault = __SEAPI('serverfault.com')
SuperUser = __SEAPI('superuser.com')
MetaStackExchange = __SEAPI('meta.stackexchange.com')
WebApplications = __SEAPI('webapps.stackexchange.com')
WebApplicationsMeta = __SEAPI('meta.webapps.stackexchange.com')
Arqade = __SEAPI('gaming.stackexchange.com')
ArqadeMeta = __SEAPI('meta.gaming.stackexchange.com')
Webmasters = __SEAPI('webmasters.stackexchange.com')
WebmastersMeta = __SEAPI('meta.webmasters.stackexchange.com')
SeasonedAdvice = __SEAPI('cooking.stackexchange.com')
SeasonedAdviceMeta = __SEAPI('meta.cooking.stackexchange.com')
GameDevelopment = __SEAPI('gamedev.stackexchange.com')
GameDevelopmentMeta = __SEAPI('meta.gamedev.stackexchange.com')
Photography = __SEAPI('photo.stackexchange.com')
PhotographyMeta = __SEAPI('meta.photo.stackexchange.com')
CrossValidated = __SEAPI('stats.stackexchange.com')
CrossValidatedMeta = __SEAPI('meta.stats.stackexchange.com')
Mathematics = __SEAPI('math.stackexchange.com')
MathematicsMeta = __SEAPI('meta.math.stackexchange.com')
HomeImprovement = __SEAPI('diy.stackexchange.com')
HomeImprovementMeta = __SEAPI('meta.diy.stackexchange.com')
MetaSuperUser = __SEAPI('meta.superuser.com')
MetaServerFault = __SEAPI('meta.serverfault.com')
GeographicInformationSystems = __SEAPI('gis.stackexchange.com')
GeographicInformationSystemsMeta = __SEAPI('meta.gis.stackexchange.com')
TeXLaTeX = __SEAPI('tex.stackexchange.com')
TeXLaTeXMeta = __SEAPI('meta.tex.stackexchange.com')
AskUbuntu = __SEAPI('askubuntu.com')
AskUbuntuMeta = __SEAPI('meta.askubuntu.com')
PersonalFinanceampMoney = __SEAPI('money.stackexchange.com')
PersonalFinanceampMoneyMeta = __SEAPI('meta.money.stackexchange.com')
EnglishLanguageampUsage = __SEAPI('english.stackexchange.com')
EnglishLanguageampUsageMeta = __SEAPI('meta.english.stackexchange.com')
StackApps = __SEAPI('stackapps.com')
UserExperience = __SEAPI('ux.stackexchange.com')
UserExperienceMeta = __SEAPI('meta.ux.stackexchange.com')
UnixampLinux = __SEAPI('unix.stackexchange.com')
UnixampLinuxMeta = __SEAPI('meta.unix.stackexchange.com')
WordPressDevelopment = __SEAPI('wordpress.stackexchange.com')
WordPressDevelopmentMeta = __SEAPI('meta.wordpress.stackexchange.com')
TheoreticalComputerScience = __SEAPI('cstheory.stackexchange.com')
TheoreticalComputerScienceMeta = __SEAPI('meta.cstheory.stackexchange.com')
AskDifferent = __SEAPI('apple.stackexchange.com')
AskDifferentMeta = __SEAPI('meta.apple.stackexchange.com')
RoleplayingGames = __SEAPI('rpg.stackexchange.com')
RoleplayingGamesMeta = __SEAPI('meta.rpg.stackexchange.com')
Bicycles = __SEAPI('bicycles.stackexchange.com')
BicyclesMeta = __SEAPI('meta.bicycles.stackexchange.com')
Programmers = __SEAPI('programmers.stackexchange.com')
ProgrammersMeta = __SEAPI('meta.programmers.stackexchange.com')
ElectricalEngineering = __SEAPI('electronics.stackexchange.com')
ElectricalEngineeringMeta = __SEAPI('meta.electronics.stackexchange.com')
AndroidEnthusiasts = __SEAPI('android.stackexchange.com')
AndroidEnthusiastsMeta = __SEAPI('meta.android.stackexchange.com')
BoardampCardGames = __SEAPI('boardgames.stackexchange.com')
BoardampCardGamesMeta = __SEAPI('meta.boardgames.stackexchange.com')
Physics = __SEAPI('physics.stackexchange.com')
PhysicsMeta = __SEAPI('meta.physics.stackexchange.com')
Homebrewing = __SEAPI('homebrew.stackexchange.com')
HomebrewingMeta = __SEAPI('meta.homebrew.stackexchange.com')
InformationSecurity = __SEAPI('security.stackexchange.com')
InformationSecurityMeta = __SEAPI('meta.security.stackexchange.com')
Writers = __SEAPI('writers.stackexchange.com')
WritersMeta = __SEAPI('meta.writers.stackexchange.com')
VideoProduction = __SEAPI('video.stackexchange.com')
VideoProductionMeta = __SEAPI('meta.video.stackexchange.com')
GraphicDesign = __SEAPI('graphicdesign.stackexchange.com')
GraphicDesignMeta = __SEAPI('meta.graphicdesign.stackexchange.com')
DatabaseAdministrators = __SEAPI('dba.stackexchange.com')
DatabaseAdministratorsMeta = __SEAPI('meta.dba.stackexchange.com')
ScienceFictionampFantasy = __SEAPI('scifi.stackexchange.com')
ScienceFictionampFantasyMeta = __SEAPI('meta.scifi.stackexchange.com')
CodeReview = __SEAPI('codereview.stackexchange.com')
CodeReviewMeta = __SEAPI('meta.codereview.stackexchange.com')
ProgrammingPuzzlesampCodeGolf = __SEAPI('codegolf.stackexchange.com')
ProgrammingPuzzlesampCodeGolfMeta = __SEAPI('meta.codegolf.stackexchange.com')
QuantitativeFinance = __SEAPI('quant.stackexchange.com')
QuantitativeFinanceMeta = __SEAPI('meta.quant.stackexchange.com')
ProjectManagement = __SEAPI('pm.stackexchange.com')
ProjectManagementMeta = __SEAPI('meta.pm.stackexchange.com')
Skeptics = __SEAPI('skeptics.stackexchange.com')
SkepticsMeta = __SEAPI('meta.skeptics.stackexchange.com')
PhysicalFitness = __SEAPI('fitness.stackexchange.com')
PhysicalFitnessMeta = __SEAPI('meta.fitness.stackexchange.com')
DrupalAnswers = __SEAPI('drupal.stackexchange.com')
DrupalAnswersMeta = __SEAPI('meta.drupal.stackexchange.com')
MotorVehicleMaintenanceampRepair = __SEAPI('mechanics.stackexchange.com')
MotorVehicleMaintenanceampRepairMeta = __SEAPI('meta.mechanics.stackexchange.com')
Parenting = __SEAPI('parenting.stackexchange.com')
ParentingMeta = __SEAPI('meta.parenting.stackexchange.com')
SharePoint = __SEAPI('sharepoint.stackexchange.com')
SharePointMeta = __SEAPI('meta.sharepoint.stackexchange.com')
MusicPracticeampTheory = __SEAPI('music.stackexchange.com')
MusicPracticeampTheoryMeta = __SEAPI('meta.music.stackexchange.com')
SoftwareQualityAssuranceampTesting = __SEAPI('sqa.stackexchange.com')
SoftwareQualityAssuranceampTestingMeta = __SEAPI('meta.sqa.stackexchange.com')
MiYodeya = __SEAPI('judaism.stackexchange.com')
MiYodeyaMeta = __SEAPI('meta.judaism.stackexchange.com')
GermanLanguage = __SEAPI('german.stackexchange.com')
GermanLanguageMeta = __SEAPI('meta.german.stackexchange.com')
JapaneseLanguage = __SEAPI('japanese.stackexchange.com')
JapaneseLanguageMeta = __SEAPI('meta.japanese.stackexchange.com')
Philosophy = __SEAPI('philosophy.stackexchange.com')
PhilosophyMeta = __SEAPI('meta.philosophy.stackexchange.com')
GardeningampLandscaping = __SEAPI('gardening.stackexchange.com')
GardeningampLandscapingMeta = __SEAPI('meta.gardening.stackexchange.com')
Travel = __SEAPI('travel.stackexchange.com')
TravelMeta = __SEAPI('meta.travel.stackexchange.com')
PersonalProductivity = __SEAPI('productivity.stackexchange.com')
PersonalProductivityMeta = __SEAPI('meta.productivity.stackexchange.com')
Cryptography = __SEAPI('crypto.stackexchange.com')
CryptographyMeta = __SEAPI('meta.crypto.stackexchange.com')
SignalProcessing = __SEAPI('dsp.stackexchange.com')
SignalProcessingMeta = __SEAPI('meta.dsp.stackexchange.com')
FrenchLanguage = __SEAPI('french.stackexchange.com')
FrenchLanguageMeta = __SEAPI('meta.french.stackexchange.com')
Christianity = __SEAPI('christianity.stackexchange.com')
ChristianityMeta = __SEAPI('meta.christianity.stackexchange.com')
Bitcoin = __SEAPI('bitcoin.stackexchange.com')
BitcoinMeta = __SEAPI('meta.bitcoin.stackexchange.com')
Linguistics = __SEAPI('linguistics.stackexchange.com')
LinguisticsMeta = __SEAPI('meta.linguistics.stackexchange.com')
BiblicalHermeneutics = __SEAPI('hermeneutics.stackexchange.com')
BiblicalHermeneuticsMeta = __SEAPI('meta.hermeneutics.stackexchange.com')
History = __SEAPI('history.stackexchange.com')
HistoryMeta = __SEAPI('meta.history.stackexchange.com')
LEGO174Answers = __SEAPI('bricks.stackexchange.com')
LEGO174AnswersMeta = __SEAPI('meta.bricks.stackexchange.com')
SpanishLanguage = __SEAPI('spanish.stackexchange.com')
SpanishLanguageMeta = __SEAPI('meta.spanish.stackexchange.com')
ComputationalScience = __SEAPI('scicomp.stackexchange.com')
ComputationalScienceMeta = __SEAPI('meta.scicomp.stackexchange.com')
MoviesampTV = __SEAPI('movies.stackexchange.com')
MoviesampTVMeta = __SEAPI('meta.movies.stackexchange.com')
ChineseLanguage = __SEAPI('chinese.stackexchange.com')
ChineseLanguageMeta = __SEAPI('meta.chinese.stackexchange.com')
Biology = __SEAPI('biology.stackexchange.com')
BiologyMeta = __SEAPI('meta.biology.stackexchange.com')
Poker = __SEAPI('poker.stackexchange.com')
PokerMeta = __SEAPI('meta.poker.stackexchange.com')
Mathematica = __SEAPI('mathematica.stackexchange.com')
MathematicaMeta = __SEAPI('meta.mathematica.stackexchange.com')
CognitiveSciences = __SEAPI('cogsci.stackexchange.com')
CognitiveSciencesMeta = __SEAPI('meta.cogsci.stackexchange.com')
TheGreatOutdoors = __SEAPI('outdoors.stackexchange.com')
TheGreatOutdoorsMeta = __SEAPI('meta.outdoors.stackexchange.com')
MartialArts = __SEAPI('martialarts.stackexchange.com')
MartialArtsMeta = __SEAPI('meta.martialarts.stackexchange.com')
Sports = __SEAPI('sports.stackexchange.com')
SportsMeta = __SEAPI('meta.sports.stackexchange.com')
Academia = __SEAPI('academia.stackexchange.com')
AcademiaMeta = __SEAPI('meta.academia.stackexchange.com')
ComputerScience = __SEAPI('cs.stackexchange.com')
ComputerScienceMeta = __SEAPI('meta.cs.stackexchange.com')
TheWorkplace = __SEAPI('workplace.stackexchange.com')
TheWorkplaceMeta = __SEAPI('meta.workplace.stackexchange.com')
WindowsPhone = __SEAPI('windowsphone.stackexchange.com')
WindowsPhoneMeta = __SEAPI('meta.windowsphone.stackexchange.com')
Chemistry = __SEAPI('chemistry.stackexchange.com')
ChemistryMeta = __SEAPI('meta.chemistry.stackexchange.com')
Chess = __SEAPI('chess.stackexchange.com')
ChessMeta = __SEAPI('meta.chess.stackexchange.com')
RaspberryPi = __SEAPI('raspberrypi.stackexchange.com')
RaspberryPiMeta = __SEAPI('meta.raspberrypi.stackexchange.com')
RussianLanguage = __SEAPI('russian.stackexchange.com')
RussianLanguageMeta = __SEAPI('meta.russian.stackexchange.com')
Islam = __SEAPI('islam.stackexchange.com')
IslamMeta = __SEAPI('meta.islam.stackexchange.com')
Salesforce = __SEAPI('salesforce.stackexchange.com')
SalesforceMeta = __SEAPI('meta.salesforce.stackexchange.com')
AskPatents = __SEAPI('patents.stackexchange.com')
AskPatentsMeta = __SEAPI('meta.patents.stackexchange.com')
GenealogyampFamilyHistory = __SEAPI('genealogy.stackexchange.com')
GenealogyampFamilyHistoryMeta = __SEAPI('meta.genealogy.stackexchange.com')
Robotics = __SEAPI('robotics.stackexchange.com')
RoboticsMeta = __SEAPI('meta.robotics.stackexchange.com')
ExpressionEngine174Answers = __SEAPI('expressionengine.stackexchange.com')
ExpressionEngine174AnswersMeta = __SEAPI('meta.expressionengine.stackexchange.com')
Politics = __SEAPI('politics.stackexchange.com')
PoliticsMeta = __SEAPI('meta.politics.stackexchange.com')
AnimeampManga = __SEAPI('anime.stackexchange.com')
AnimeampMangaMeta = __SEAPI('meta.anime.stackexchange.com')
Magento = __SEAPI('magento.stackexchange.com')
MagentoMeta = __SEAPI('meta.magento.stackexchange.com')
EnglishLanguageLearners = __SEAPI('ell.stackexchange.com')
EnglishLanguageLearnersMeta = __SEAPI('meta.ell.stackexchange.com')
SustainableLiving = __SEAPI('sustainability.stackexchange.com')
SustainableLivingMeta = __SEAPI('meta.sustainability.stackexchange.com')
Tridion = __SEAPI('tridion.stackexchange.com')
TridionMeta = __SEAPI('meta.tridion.stackexchange.com')
ReverseEngineering = __SEAPI('reverseengineering.stackexchange.com')
ReverseEngineeringMeta = __SEAPI('meta.reverseengineering.stackexchange.com')
NetworkEngineering = __SEAPI('networkengineering.stackexchange.com')
NetworkEngineeringMeta = __SEAPI('meta.networkengineering.stackexchange.com')
OpenData = __SEAPI('opendata.stackexchange.com')
OpenDataMeta = __SEAPI('meta.opendata.stackexchange.com')
Freelancing = __SEAPI('freelancing.stackexchange.com')
FreelancingMeta = __SEAPI('meta.freelancing.stackexchange.com')
Blender = __SEAPI('blender.stackexchange.com')
BlenderMeta = __SEAPI('meta.blender.stackexchange.com')
MathOverflow = __SEAPI('mathoverflow.net')
MathOverflowMeta = __SEAPI('meta.mathoverflow.net')
SpaceExploration = __SEAPI('space.stackexchange.com')
SpaceExplorationMeta = __SEAPI('meta.space.stackexchange.com')
SoundDesign = __SEAPI('sound.stackexchange.com')
SoundDesignMeta = __SEAPI('meta.sound.stackexchange.com')
Astronomy = __SEAPI('astronomy.stackexchange.com')
AstronomyMeta = __SEAPI('meta.astronomy.stackexchange.com')
Tor = __SEAPI('tor.stackexchange.com')
TorMeta = __SEAPI('meta.tor.stackexchange.com')
Pets = __SEAPI('pets.stackexchange.com')
PetsMeta = __SEAPI('meta.pets.stackexchange.com')
AmateurRadio = __SEAPI('ham.stackexchange.com')
AmateurRadioMeta = __SEAPI('meta.ham.stackexchange.com')
ItalianLanguage = __SEAPI('italian.stackexchange.com')
ItalianLanguageMeta = __SEAPI('meta.italian.stackexchange.com')
StackOverflowemPortugu234s = __SEAPI('pt.stackoverflow.com')
StackOverflowemPortugu234sMeta = __SEAPI('meta.pt.stackoverflow.com')
Aviation = __SEAPI('aviation.stackexchange.com')
AviationMeta = __SEAPI('meta.aviation.stackexchange.com')
Ebooks = __SEAPI('ebooks.stackexchange.com')
EbooksMeta = __SEAPI('meta.ebooks.stackexchange.com')
Beer = __SEAPI('beer.stackexchange.com')
BeerMeta = __SEAPI('meta.beer.stackexchange.com')
SoftwareRecommendations = __SEAPI('softwarerecs.stackexchange.com')
SoftwareRecommendationsMeta = __SEAPI('meta.softwarerecs.stackexchange.com')
Arduino = __SEAPI('arduino.stackexchange.com')
ArduinoMeta = __SEAPI('meta.arduino.stackexchange.com')
CS50 = __SEAPI('cs50.stackexchange.com')
CS50Meta = __SEAPI('meta.cs50.stackexchange.com')
edxcs1691x = __SEAPI('edx-cs169-1x.stackexchange.com')
edxcs1691xMeta = __SEAPI('meta.edx-cs169-1x.stackexchange.com')
Expatriates = __SEAPI('expatriates.stackexchange.com')
ExpatriatesMeta = __SEAPI('meta.expatriates.stackexchange.com')
MathematicsEducators = __SEAPI('matheducators.stackexchange.com')
MathematicsEducatorsMeta = __SEAPI('meta.matheducators.stackexchange.com')
MetaStackOverflow = __SEAPI('meta.stackoverflow.com')
EarthScience = __SEAPI('earthscience.stackexchange.com')
EarthScienceMeta = __SEAPI('meta.earthscience.stackexchange.com')
InterpersonalSkills = __SEAPI('interpersonal.stackexchange.com')
InterpersonalSkillsMeta = __SEAPI('interpersonal.meta.stackexchange.com')
