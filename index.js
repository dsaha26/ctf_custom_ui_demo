
// the difference between the two projects:

// TG Test Runner has internal Test Flows
// it therefore only uses singular CTF Test Action
// its test_data configs are loaded at Test level
// it therefore cannot tie them to Test Setup level in CTF, only Test level

// NO TEST SETUP CONFIG LAYER

// flow:
// user picks Test Setup in CTF
// user picks Test from CLI options, pick github repo, branch/tag/hash
// user picks Test Data for the Test
// user can edit (some of) the Test config
// user can fill out the Custom UI card


// DTF has no Test Flows
// it expects a CTF Test to have multiple Test Actions
// therefore its tests folder is really a test actions folder
// it allows configs set at Test Setup level in CTF
// it does not need Test level configs

// NO TEST CONFIG LAYER

// flow:
// user picks Test Setup in CTF
// user can edit (some of) the Test Setup config
// user picks Test from CLI options, pick github repo, branch/tag/hash
// user picks Test Data

repos = {
    "dtf": {
        "path": "dtf", // url
        "test_setups_include": [ "test_setups/**/test_setup_data" ],
        "tests_include": [ "tests/**/test_data" ]
    },
    "tg_test_runner": {
        "path": "tg_test_runner", // url
        "test_setups_include": [ "test_setups/**/test_setup_data" ],
        "tests_include": [ "tests/**/test_data" ]
    },
}

// APIs needed

// NOTE:
// hash is too open ended IMO.. tag serves as a named hash
// how would users pick from any hash in the repo anyway??

// background async task
//  can optionally use Celery library in API server now!
//  every _x_ min, API server should be pulling on its local copy of the git repos for teams to keep them up to date
//  it should NOT check out anything.. git clone should use --bare

// GET list of github repo's branches and tags for [team name]
//  called.. every time page is loaded??
// POST [branch or tag or hash] request default json file (with embedded schema) for Test Setup [name]
//  called after Test Setup is selected
//  may return empty.. (for TG will be empty).. which is ok, no action
//  if returns options, then auto switch the Env Vars to Custom UI mode and show the options
//      disable the mode toggle too, because switching 1) serves no benefit and 2) could break the Test
// POST [branch or tag or hash] request default json file (with embedded schema) for Test Action [name]
//  called after Test Action is selected
//  may return empty.. (for DTF will be empty).. which is ok, no action
//  if returns options, then auto switch the Env Vars to Custom UI mode and show the options
//      disable the mode toggle too, because switching 1) serves no benefit and 2) could break the Test

// these APIs should check out a local copy of a bare git repo that API server maintains
//   at the requested branch or tag.. or return error if not exist, somehow
//   this gets a clean folder to work in
//   then they run the scraping routing found in this demo repo for finding configs, which works for TG or DTF style
//   then clean up the checked out repo before API return
