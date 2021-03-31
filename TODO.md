# TODO


-   **code cleanup**

    Write better ideomatic code. Srsly. Nobody needs to know who's more
    at home with assembler and C than Python. Also, add error handling.

    DRY!! There's too much duplicated code

-   properly daemonize the bot

    Create a wrapper script to capture STDOUT and STDERR into log files,
    a .service file, and a logrotate entry. Add an install script/playbook?

-   Cache alt name to profile ID mappings

-   multiple guild support

    Generalize the bot to support per-server/guild configurations. Due to
    the sensitive nature of the dedicated alt(s), this is tricky.

-   support large numbers of alts

    The **active** command is limited to the length of the contact
    list, i.e. 150 characters. Future use/commands may exceed this
    limit and require multiple dedicated alts.

-   implement reference commands

    Save a trip to the wiki, e.g. query item info, look up
    location coordinates, give directions (maybe including
    free running lanes), ...

    ^^^ partially done, work in progress

-   more detailed profile information

    Maybe display more detailed character info than EE's !profile
    command does.

-   track character changes

    Go nuts, use a database to track character changes (group tag, XP,
    description, ...)

-   commands to maintain the contact list

    Admin-level commands to manipulate the alt's contact list.
    Add/remove individual alts, change contact color, import 
    MassContacts list.

-   command to export the contact list in MassContacts form

    Ditto. 

-   **version** command

    Show the tag/commit ID. Because, why not?

-   **code** command

    Print a link to the Github page.


