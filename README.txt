#####################
#  Raffle Minigame  #
#####################

Description: Allow users to start a raffle for currency. By default one user wins although more winners can be specified. Options in UI
Made By: GeneralPattonBS
Website: https://www.twitch.tv/generalpattonbs

#####################
#     Versions      #
#####################
1.2.0.0
    - Added the ability for more than one winner of the raffle
    - Added better input sanitization

1.1.0.0
    - Fixed a bug which only allowed the first half of users that joined to win
    - Added an option to allow multiple joins or not

1.0.0.0 
    - Initial release

#####################
#      Usage        #
#####################

!raffle <amount> <winners>
Starts a raffle for the given amount with a set number of winners.
If winners is not specified it will default to one winner.

!join
Joins an active raffle