import yargs from 'yargs'
import { hideBin } from 'yargs/helpers'

const parser = yargs(hideBin(process.argv))
    .command(
        'test_suite <name>',
        'Get test suite json with schema',
    )

const args = parser.parse()

const foo = 1
