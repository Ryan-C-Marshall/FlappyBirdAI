import math
import random

import pygame
from pygame.locals import *

pygame.init()

# Declare colours, images, sounds, fonts, variables

AI_TEST_VALUE = 0

BACKGROUND_COLOUR = (67, 151, 199)
GAME_WIDTH = 800
GAME_HEIGHT = 600

font = pygame.font.Font('freesansbold.ttf', 32)

CHARACTER_WIDTH = 40
CHARACTER_HEIGHT = 40

PIPE_WIDTH = 30
PIPE_SEPARATION = 300

INITIAL_X_VEL = 5

###
PLAYER_ICON = pygame.image.load("bird.png")
PLAYER_ICON = pygame.transform.scale(PLAYER_ICON, (CHARACTER_WIDTH * 1.5, CHARACTER_HEIGHT * 1.5))

background = pygame.image.load("flappyBirdBackground.png")
background = pygame.transform.scale(background, (GAME_WIDTH, 400))
###

fps = pygame.time.Clock()
window = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))


class Pipe:

    def __init__(self, xPosition, yGapPosition, gapHeight, colour):
        self.xPosition = xPosition
        self.yGapPosition = yGapPosition
        self.gapHeight = gapHeight
        self.colour = colour
        self.passedPlayer = False

    def draw(self):
        # top pipe
        pygame.draw.rect(window, self.colour, (self.xPosition, 0, PIPE_WIDTH, self.yGapPosition))

        # top pipe cap
        # pygame.draw.rect(window, self.colour * 0.8, ())

        # bottom pipe
        topOfPipe = self.yGapPosition + self.gapHeight
        pygame.draw.rect(window, self.colour, (self.xPosition, topOfPipe, PIPE_WIDTH, GAME_HEIGHT - topOfPipe))

    def move(self, velocity):
        self.xPosition += velocity

    def playerHitsRect(self, playerHitboxRect):
        topRect = pygame.Rect(self.xPosition, 0, PIPE_WIDTH, self.yGapPosition)
        bottomRect = pygame.Rect(self.xPosition, self.yGapPosition + self.gapHeight, PIPE_WIDTH,
                                 GAME_HEIGHT - self.yGapPosition + self.gapHeight)
        return pygame.Rect.colliderect(playerHitboxRect, topRect) or pygame.Rect.colliderect(playerHitboxRect,
                                                                                             bottomRect)

    def playerHits(self, xPos, yPos):
        ellipseWidthRad = CHARACTER_WIDTH * 1.3 / 2
        ellipseHeightRad = CHARACTER_HEIGHT * 1.1 / 2
        ellipseX = xPos - int(CHARACTER_WIDTH / 5) + ellipseWidthRad
        ellipseY = yPos - (CHARACTER_HEIGHT / 15) + ellipseHeightRad
        return self.pointUnderEllipse(-1, ellipseWidthRad, ellipseHeightRad, ellipseX, ellipseY, self.xPosition,
                                      self.yGapPosition) \
               or self.pointUnderEllipse(-1, ellipseWidthRad, ellipseHeightRad, ellipseX, ellipseY,
                                         self.xPosition + PIPE_WIDTH, self.yGapPosition) \
               or self.pointUnderEllipse(1, ellipseWidthRad, ellipseHeightRad, ellipseX, ellipseY, self.xPosition,
                                         self.yGapPosition + self.gapHeight) \
               or self.pointUnderEllipse(1, ellipseWidthRad, ellipseHeightRad, ellipseX, ellipseY,
                                         self.xPosition + PIPE_WIDTH, self.yGapPosition + self.gapHeight)

    def pointUnderEllipse(self, concavity, widthRad, heightRad, xCenter, yCenter, xPoint, yPoint):
        try:
            return concavity * (yPoint - yCenter) <= math.sqrt((heightRad ** 2) *
                                                               (1 - (((xPoint - xCenter) ** 2) / (widthRad ** 2))))
        except ValueError:
            return False


class AIPlayer:

    def __init__(self, weights: list[list[list[float]]], constants: list[list[float]], testValue: int):
        self.weights = weights
        self.constants = constants
        self.testValue = testValue

        # Weights = [ (matrices) [[ 0 (cols) x 1 (rows) ]], [[ 1 x 2 ]], ... ]
        # matrix example for input layer = 2, hidden = 4: [ [0.5, 0.01], [0.333, 0.5], [0.2, 0.3], [0.125, 0.85] ]
        # Constants = [ [ constant list l2 ], [ constant list l3 ], [ len = len(l4) = len(weights[3]) ] ]

    def compute(self, inputs: list[float]) -> list[float]:
        layer = inputs.copy()
        # for i in range(len(inputs)):
        #     layer.append(math.atan(inputs[i] / 50) * 2 / math.pi)

        for i in range(len(self.weights)):
            layer = self.nextLayer(layer, self.weights[i], self.constants[i])

        return layer

    def nextLayer(self, layer: list[float], matrix: list[list[float]], constants: list[float]) -> list[float]:
        nextLayer = []
        for i, row in enumerate(matrix):
            nextLayer.append(
                math.atan(sum([matrix[i][j] * layer[j] for j in range(len(layer))]) + constants[i]) * (2 / math.pi)
            )

        return nextLayer


class Species:

    def __init__(self, genSize, firstGenSize, inputSize, outputSize):
        self.outputSize = outputSize
        self.inputSize = inputSize
        self.genSize = genSize

        self.generationNum = 0
        self.currentGeneration = [generatePlayer([inputSize, inputSize * 2, inputSize * 2, inputSize * 2, outputSize])
                                  for _ in range(firstGenSize)]
        self.reps = 15

    def train(self, generations):
        topPlayers = []
        topScores = []

        for _ in range(generations):
            scores = self.testGeneration()
            newGeneration = []

            print("Top players in " + str(self.generationNum) + ":\n")
            for i in range(int(math.sqrt(self.genSize) / 2)):
                topScore = max(scores)
                topPlayer = self.currentGeneration[scores.index(max(scores))]
                playerRank = [score > topScore for score in topScores].count(True)
                topPlayers.insert(playerRank, topPlayer)
                topScores.insert(playerRank, topScore)
                if len(topPlayers) > 5:
                    topPlayers.pop()
                    topScores.pop()

                print("Brain: " + str(topPlayer.weights) + ", " + str(topPlayer.constants))
                print("Score: " + str(max(scores)) + "\n")

                self.currentGeneration.pop(scores.index(max(scores)))
                scores.remove(max(scores))

            print("Top players (ever):")
            for i in range(len(topPlayers)):
                print("Brain: " + str(topPlayers[i].weights) + ", " + str(topPlayers[i].constants))
                print("Score: " + str(topScores[i]) + "\n")

            for _ in range(self.genSize):
                p1Index = int((random.random() ** 2) * len(topPlayers))
                p2Index = p1Index
                while p2Index == p1Index:
                    p2Index = int((random.random() ** 2) * len(topPlayers))

                newGeneration.append(self.breed(topPlayers[p1Index], topPlayers[p2Index]))

            self.currentGeneration = newGeneration
            self.generationNum += 1

    def testGeneration(self):
        scores = []

        for player in self.currentGeneration:
            plScore = 0

            for _ in range(self.reps):
                plScore += play(True, False, player) / self.reps

            scores.append(plScore)
            print("\rCompleted " + str(len(scores)) + " players.", end="")

        print("Completed " + str(len(scores)) + " players.")
        return scores

    def breed(self, player1: AIPlayer, player2: AIPlayer):
        spermBrain = player1.weights
        childBrain = [[row.copy() for row in matrix] for matrix in spermBrain]
        childConstants = [arr.copy() for arr in player1.constants]

        for i, matrix in enumerate(spermBrain):
            for j, row in enumerate(matrix):
                for k in range(len(row)):
                    gene1 = player1.weights[i][j][k]
                    gene2 = player2.weights[i][j][k]
                    childBrain[i][j][k] = (gene1 + gene2) / 2 + (gene1 - gene2) * (3 * random.random() - 1.5) ** 2
                    # the average of the two, plus [-0.5, 0.5] * their difference ^ 2

        for i in range(len(childConstants)):
            childConstants[i] = [(player1.constants[i][j] + player2.constants[i][j]) / 2 +
                                 (random.random() - 0.5) * (player1.constants[i][j] - player2.constants[i][j])
                                 for j in range(len(player1.constants[i]))]
            # the average of the two parents, + [-0.5, 0.5] * their difference squared

        return AIPlayer(childBrain, childConstants, AI_TEST_VALUE)


def generatePlayer(layerSizes):
    return AIPlayer(
        [generateMatrix(layerSizes[i], layerSizes[i + 1], - 5 * random.random() + 5)
         for i in range(len(layerSizes) - 1)],

        [[- 5 * random.random() + 5 * (random.random() - 0.5) for _ in range(layerSizes[i + 1])]
         for i in range(len(layerSizes) - 1)],

        AI_TEST_VALUE
    )


def generateMatrix(fromSize, toSize, multiplier):
    return [[multiplier * (random.random() - 0.5) for _ in range(fromSize)] for _ in range(toSize)]


def spawnPipe(score, pipes):
    # pipes spawn PIPE_WIDTH + 50 to the right of the screen so that they can smoothly flow onto the screen
    gapHeightUppBound = int((4100 / (score + 40))) + 85
    gapHeightLowBound = int(820 / (score + 40)) + 75
    gapHeight = random.randint(gapHeightLowBound, gapHeightUppBound)
    yGapPosition = random.randint(int(0.1 * GAME_HEIGHT), int(0.9 * GAME_HEIGHT) - gapHeight)
    newPipe = Pipe(GAME_WIDTH + 50, yGapPosition, gapHeight, (50, 50, 130))
    pipes.append(newPipe)


def drawText(text, x, y):
    text = font.render(text, True, (255, 255, 255), (67, 151, 199))
    textRect = pygame.Rect(x, y, 0, 0)
    window.blit(text, textRect)


# Main game loop


def play(AI, draw, player) -> int:
    onGround = False
    doubleJumpAvailable = False

    pipes = []

    upKey = False

    X_POS = 250
    yPos = 0
    xVel = 5
    yVel = 0

    backgroundX = 0

    alive = True
    score = 0

    GRAVITY_ACCELERATION = 0.5

    quitGame = False

    while not quitGame and alive:

        # Process events
        AIValue = 0
        if AI:
            vertDistanceTop = 0
            vertDistanceBottom = 0
            horDistance = 0

            for pipe in pipes:
                if not pipe.passedPlayer:
                    vertDistanceTop = pipe.yGapPosition - yPos
                    vertDistanceBottom = pipe.yGapPosition + pipe.gapHeight - yPos
                    horDistance = pipe.xPosition - X_POS
                    break

            inputs = [
                vertDistanceTop,
                vertDistanceBottom,
                horDistance,
                yVel,
                xVel
            ]

            AIValue = player.compute(inputs)[0]
            upKey = AIValue > player.testValue
            pygame.event.pump()

        else:
            for event in pygame.event.get():
                if event.type == QUIT:
                    quitGame = True
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        quitGame = True
                    else:
                        upKey = True
                elif event.type == KEYUP:
                    upKey = False

        # perform calculations, update your variables accordingly

        # check if on ground
        onGround = False
        if yPos + CHARACTER_HEIGHT >= GAME_HEIGHT:
            onGround = True

        # check if hitting a pipe
        # old hitbox: playerHitbox = pygame.rect.Rect(X_POS, yPos, CHARACTER_WIDTH, CHARACTER_HEIGHT)
        for pipe in pipes:
            if pipe.playerHits(X_POS, yPos):
                alive = False
                break

        # update player kinetics
        if upKey:
            yVel = -7

        yVel += GRAVITY_ACCELERATION
        yPos += yVel
        if onGround and yVel > 0:
            yPos = GAME_HEIGHT - CHARACTER_HEIGHT

        xVel = math.sqrt(score / 12) + INITIAL_X_VEL

        # maybe spawn or delete pipes, then move them all
        if len(pipes) == 0 or pipes[-1].xPosition <= GAME_WIDTH + 50 - PIPE_SEPARATION:
            # pipes[-1] is the last (most recently added) pipe
            spawnPipe(score, pipes)

        if pipes[0].xPosition + PIPE_WIDTH + 50 < 0:  # if the least recently added pipe is significantly off the screen
            pipes.pop(0)

        for pipe in pipes:
            pipe.move(-xVel)

        # increase the score?
        for pipe in pipes:
            if not pipe.passedPlayer and (pipe.xPosition + PIPE_WIDTH) < X_POS:
                score += 1
                pipe.passedPlayer = True
                break

        if draw:
            # update the background
            ###
            backgroundX -= xVel
            if backgroundX <= -GAME_WIDTH:
                backgroundX += GAME_WIDTH

            # draw the graphics
            window.fill(BACKGROUND_COLOUR)
            ###

            ###
            window.blit(background, (backgroundX, 200))
            window.blit(background, (backgroundX + GAME_WIDTH, 200))

            window.blit(PLAYER_ICON, (X_POS - 16, yPos - 18))

            # pygame.draw.rect(window, (255, 255, 255), (X_POS, yPos, CHARACTER_WIDTH, CHARACTER_HEIGHT))  # player
            # pygame.draw.ellipse(window, (255, 255, 255),
            #                     (X_POS - int(CHARACTER_WIDTH / 5), yPos - (CHARACTER_HEIGHT / 15),
            #                      int(CHARACTER_WIDTH * 1.3), int(CHARACTER_HEIGHT * 1.1)))

            pygame.draw.ellipse(window, (100, 100, 255),
                                (X_POS - int(CHARACTER_WIDTH / 5) + CHARACTER_WIDTH * 1.3 * 0.5,
                                 yPos - (CHARACTER_HEIGHT / 15) + CHARACTER_HEIGHT * 1.1 * 0.5, 3,
                                 3))
            ###

            drawText(str(score), 400, 25)

            for pipe in pipes:
                pipe.draw()

            pygame.display.update()
            fps.tick(25)

    return score


myPlayer = AIPlayer([[[-0.8287384722097234, -0.4983956574830908, 0.16041609778704513, 2.292457169067424,
                       -0.22916502096662775],
                      [0.7958941262600803, -0.608172583619396, 0.2555399359901347, 0.6748862107490099,
                       0.7920488115502391],
                      [0.04521859126430253, 1.4956274295329925, -2.6876570041338237, 2.3609370704754014,
                       1.5338331753548533],
                      [-1.7890809601810547, -1.5561371637821375, 1.8158235176624196, 3.6703021126440047,
                       0.31532139322478586],
                      [0.5501225280628788, 4.899702463490511, 0.024972267666494286, 0.10461602483225235,
                       0.2559859198795272],
                      [0.1675088203629975, -0.5295118810705699, -2.4424074939035822, 0.7072215752096415,
                       0.18826051183244055],
                      [-1.6450874029878635, -1.6509656410554223, -0.04042199102622587, -0.6865193711216894,
                       0.35281881523016334],
                      [0.41405021806873143, 0.42053231711831385, -0.05935420604226903, 0.05126837162365597,
                       0.9713016067872604],
                      [2.4953590051261916, 0.4132953459016372, -0.2790616784017722, -4.244683561060618,
                       1.9196008864941498],
                      [0.40410131219901824, -0.28889311254183436, 0.18855576102156088, -1.0860178076016629,
                       0.583316257313597]], [
                         [1.3299927195212053, -2.7413389520315, 9.935126779233073, -4.4295271500611415,
                          -1.666726453736227, -0.47270640713168394, 1.1572393129187166, 4.3024018256972445,
                          2.2854032046447412, 1.6336315808651565],
                         [-3.2541332080427607, 0.19120850794698185, -0.48363163112573526, 1.1711490940057212,
                          0.3454301861092894, -1.0615202102247603, -14.0617431903976, -0.07412966527274989,
                          1.746668252233625, 0.9627680995530439],
                         [-0.0013145701316296752, 0.2958078503312377, -0.9936138879815711, -0.5938151775771908,
                          -3.7403594309984105, 9.180846528081064, -2.5029940411495812, 0.4461522183375709,
                          -1.3965230851437855, -0.6927107471919025],
                         [2.3672106478538906, 0.7234054717031592, 6.079729226642089, 0.09761599402133353,
                          0.16142537427530113, -4.27701600013439, -1.489013069176162, 0.14466367961023516,
                          2.7596671448453605, -5.6905113924431445],
                         [0.8819754965376241, 0.1356665135133755, -8.22249931913182, 1.8194437905199505,
                          -2.372964328224881, 22.997480755582295, 0.21210930529329597, -2.870766487545148,
                          0.09064033442522149, 0.7046193451217793],
                         [-1.325090651380168, -0.2922180688134467, -2.4506437996374335, 0.8174157857076187,
                          -0.26769076471251696, -1.1892405519790223, -0.36699133419840585, -1.5733510121809,
                          0.33050119784784493, -1.5599361313542879],
                         [0.5716649369874485, -6.113247267014852, -0.19990238429163998, -0.5474617574276048,
                          0.62551378019883, -3.3792472375220237, -0.6781869173575067, 0.3505896027585699,
                          6.64454801530432, 3.7472327191685473],
                         [0.9236652267168604, 10.966515638065662, 0.6434182339713831, -0.62231654478705,
                          0.7693160293609327, 0.42281883915393453, -1.0950785325221402, -1.0600439349212751,
                          -2.8402441451909732, 0.05444346503336984],
                         [0.29168541154465805, 3.791103791890818, -0.47900358394402864, -1.2365187579856975,
                          -0.8161066570064645, 6.389358320500257, -1.2632468297166153, -9.691554836946954,
                          0.5094643014418171, 4.304397625309671],
                         [0.24470586836982644, 1.363043255259666, -0.47139371125846485, -3.8704997521472713,
                          1.4036729611676835, -0.0173492317524012, 22.110981310969542, 0.9802175691907584,
                          -0.08059556274861579, -5.113392474786554]], [
                         [-1.4966657049503815, 0.0987846990968323, 0.5161532638173942, -1.2412588382458485,
                          -0.3972096028515847, 3.935863603998368, 0.10181461897545852, -43.87266148787384,
                          3.139541645013875, -1.8518150098558963],
                         [0.35266279126096506, 7.421621407954413, 1.612533545900468, 5.724531110861543,
                          2.4384671902093973, -1.0188135953808017, 3.3574425453486882, -0.970999884597385,
                          0.6957192925083041, -2.7851073658561827],
                         [-0.4951852348229188, -0.19740383913439952, -0.8726838460627134, 5.488024591567889,
                          -0.11425480705310405, -1.8473294031844878, -0.5493591677492751, -2.244723417263026,
                          1.7063052939580952, -1.604594368878861],
                         [0.9644348369952797, -0.425030431170541, -0.20920565627820614, 0.8797272610550516,
                          1.3930377567331946, 0.7897407726050196, -2.446197058785878, 4.043245668418651,
                          1.4172656312640906, 8.262976286756043],
                         [-3.2547254019832623, 1.9950224311330362, 0.8019817999725835, -0.5931454890471829,
                          3.980440027897849, -2.141929112106734, 3.3813610855630927, -0.34432711383492615,
                          0.22522325930890688, 0.5338101179863144],
                         [1.9219309205683328, 1.4305555073177962, 0.3592715826969822, 0.18653133876480632,
                          -0.4584615012216915, -0.6348572433639454, 0.9003925566955878, 2.274482846627804,
                          -0.3979617451939648, -1.0405481131290875],
                         [3.239290035936562, -4.48095127977331, 0.41286383042294705, -1.0808984318013009,
                          -0.5496191545903368, -0.8447147709019549, 1.5756765224068512, 1.5645311000173436,
                          3.203497695424849, -1.5872161937348626],
                         [-13.031104085314324, -0.7311038578689866, -7.804675635459604, -0.9612642286578711,
                          2.9181089414349763, -5.031492122049565, -0.9720575533141568, -0.9223110747906479,
                          1.5428926375567809, -1.8919567438723888],
                         [1.4620037689921122, 0.7163671883532083, 2.8575305782949303, 0.7331644383128209,
                          1.9988232581868628, 0.6530281806015248, -5.88671678436999, 23.78539088585137,
                          -0.20555771871012973, -6.936749695637773],
                         [0.3968579744404698, 7.566086577608106, -4.3847107559124, -0.9743592171452141,
                          2.5566752491344076, -0.5346336915132175, 5.376110389204965, 0.5494462021993866,
                          -1.6767957008667522, -5.777828676373106]], [
                         [0.6709317364749332, -2.969075781103081, -0.4238218788835968, 1.1058323644076462,
                          0.6444872411620324, 0.26266553471689635, 1.1686687647015503, 1.0069462860803,
                          -1.9250579846445302, 0.21797234411857255]]], [
                        [-3.2682948980572837, -4.120744784478535, -3.1363352498805326, -6.234507642710816,
                         -4.625401754064231, -2.5796187954411134, -1.148807494164288, -2.771111890537135,
                         -4.367391467475085, -2.5852438578401142],
                        [-2.470237458421242, -2.04118691896554, -0.5213963301813346, -2.829323442795915,
                         -1.0565486746377513, -2.6585715884848082, 1.4735479206989328, -1.0760395614739662,
                         -0.6096855238782222, -2.4619187724809533],
                        [-1.8283671598734295, -1.8431878008494351, -2.64448071560822, -0.5952320057989553,
                         -4.70317236243693, -2.7112620889012056, -2.7593897853992204, -2.503239919957726,
                         -2.9657104303169666, -1.1114634640063268], [-0.6946873058351641]]
                    , AI_TEST_VALUE)
for _ in range(100):
    print(play(True, False, myPlayer))

myPlayer = AIPlayer([[[0.12230928503327927, 0.26421152714355894, 0.49455484121995563, -0.2911784674623097,
                       0.7283539202370846],
                      [0.3292820496043161, 0.25840129542686563, -0.1192085170029178, 0.5773438360966744,
                       -0.3745894787176978],
                      [-0.3166004068237835, 0.5126085383660441, -0.1348268067257569, -0.17482997126935812,
                       0.2598374340648293],
                      [0.11852988683303498, 0.6099107335991838, -0.18474390747592753, -0.3341472808942264,
                       0.5235709766665486],
                      [0.6253658820618124, 0.1584275115634625, -0.19549597007701053, 0.2992329536648766,
                       -0.12442419946022437],
                      [-0.0353355880737454, -0.5480009875996468, 0.19372553844283402, -0.4134441908769714,
                       0.1428000974387965],
                      [-0.6027444977059265, -0.052612557118786187, -0.1298111029704059, 0.5794391440637042,
                       0.1991408009683357],
                      [-0.3672032996592712, -0.11952457061371409, -0.09559791104478371, 0.381911929588291,
                       -0.38720233092166323],
                      [-0.48538293061740806, -0.10237803597767672, -0.3937760162506274, -0.3388993779068552,
                       -0.5068146549049087],
                      [-0.5459802926731919, 0.49505146786634446, 0.37991682344818595, -0.00983340492198356,
                       -0.1625333918518857]], [
                         [-1.1177448882121566, 0.029546548614152953, 0.38641347169518137, 0.018452779500255912,
                          -0.10529370706536845, 0.4863334133297102, 0.6910891267051966, -0.5421984078713108,
                          0.1326154223247382, 0.27433668498323877],
                         [-0.5371021562822953, 1.0267793492580521, -0.6807924100470178, 0.4202946761270856,
                          -0.039645572772921245, -0.17665256730279494, 0.3215740819823891, -1.0765667549206537,
                          -0.9545326750096524, -0.1586441593237134],
                         [-0.08002441212134395, 0.8270897550789789, 1.1397072663408987, 0.32196875883947584,
                          -0.5986830563766278, -0.7270356752190444, 1.244761785712079, 0.19171020332739658,
                          0.2076131393181, 0.568478026787685],
                         [-0.15467911484483426, -1.0314689155742083, -0.30199257685471037, -0.4198491227789931,
                          0.4867351703487707, -0.479344251817354, 0.045119825187526365, -1.0281791047994258,
                          -0.056911005158299284, -0.2675781215458195],
                         [-0.2638401154365803, -0.9875141778205265, 0.46703181681162276, 0.34763116365885427,
                          1.2439143628786755, 0.32008776986454185, -0.6643473466535449, -0.22085269610544978,
                          0.4914650453553468, -0.2560719325546563],
                         [-0.38597395272291307, -0.20123437209509795, -0.8847813015057574, 0.33349744885998306,
                          0.1881548884503048, -0.39034104321007357, 0.5727489836756244, -0.25210330622005406,
                          -0.1681864345659043, 0.777079565653429],
                         [-1.237728991026512, -0.8029159351772054, 0.46417618167987407, 0.6282932073294833,
                          0.9871756264710159, -1.2455254514272676, 0.45248187187542127, -0.3572947121492887,
                          0.8066020768862969, 0.5094643440104637],
                         [0.4659057834690877, 0.23090422219565312, -0.6726153376831945, 0.13406253077457164,
                          -0.4882270948776501, -0.7963594961539614, 0.7697665556507167, -0.8211930742031516,
                          0.44524702775169994, 0.1646156925434964],
                         [-0.4577031677534855, 0.16711699619326403, -0.17850224818382007, 0.22912253396439222,
                          0.677429641860416, 0.17708977751722707, -0.15475181384979267, -0.48913117238240844,
                          -0.9575871666113556, -0.6576668196554726],
                         [-0.6485960483741853, -0.060240587402944204, -0.8381689081820196, 0.6143093936146397,
                          -1.1258002355211914, -1.01496922748776, -0.3194793324195247, 0.9993061691983266,
                          0.3316664051844925, -0.19099010988660223]], [
                         [0.2481366829881762, 0.7530919283933809, 1.6659010304019684, -0.37958106168848044,
                          -0.04651147589137293, 0.1607562228561286, -1.6555385585455449, 0.40071655642973153,
                          -1.7770781114583043, -0.017691355902041336],
                         [0.2400344833023417, -1.2421623186802706, -0.9940243592103062, -0.47997208314839485,
                          -0.7973572070714994, -1.450905521581405, 0.18267967748094954, 1.1831541586548435,
                          -1.443238100187266, 1.4196711209964237],
                         [-0.11669350852100925, 1.1932663890881632, 0.4104282751749278, 0.783934194094688,
                          -0.8989715887006408, -1.023213680606141, 0.399778973158237, -1.255816770548252,
                          -0.8718019354808366, -1.3225108251559976],
                         [-0.22058399431192813, 0.41895218300452275, 1.219963284131941, 1.7701563045936561,
                          -0.9830798346656866, -1.446914025332665, 1.2177061680925625, 0.1484728553637434,
                          -0.5099851811528741, 1.1254771868867106],
                         [-0.2953527206240985, 0.5172344261827462, 0.8694817974263881, 0.8352755298205101,
                          0.6010503102319865, -0.7159006821973242, 0.8461949367282494, 0.657196995434814,
                          1.1570254603932146, -1.8624913197122535],
                         [-1.3778682024752233, 0.8546262943170876, 0.31922246010526995, 1.368669619095866,
                          0.10714274646874272, -0.9000325595027495, -1.4377077773908495, 0.5703620040737574,
                          1.0780118250838933, 0.32682708129138505],
                         [-0.9965896376524133, 0.7041699412640566, -0.5368921170592347, 1.341461990178787,
                          -0.5108984689667058, -0.9762382707153181, -0.3620557556124081, -0.07354720188921002,
                          0.8657049869687209, -0.9530997957635484],
                         [0.6166352269881951, -0.6119260820885306, 1.491823807675521, -1.1044389996821655,
                          0.32859419783560595, -1.0347369334212275, 1.0829883714124586, 0.6637196998003425,
                          1.095429469040496, 0.8223544265561467],
                         [-1.2884602769595543, 1.707717461326548, -0.5465473454805749, 1.4060354448596288,
                          -1.2709620573616782, 0.5731627977526221, 0.15514716108612298, -0.8176108966890566,
                          0.3941451638061759, -1.2650404911732969],
                         [0.9281201708948159, -1.3838115502077128, -0.3397611503312582, -0.19175069780342144,
                          -1.3916085452451779, 1.0235057057273136, 1.5924762605571543, -0.11387558366899803,
                          0.6355604636240668, -0.16008924274736977]], [
                         [0.0557882937492602, 0.5942051910302625, 0.8891545009762076, -1.367294900476931,
                          -0.005671638641362902, -0.9092018944474859, -0.8628359924848453, 0.5074765513880206,
                          -0.12004335504353386, -1.0131715197404993]]],
                    [[-3.198798800046604, -1.50619993485625, -0.08993417734094032, -3.576311446663202,
                      -2.357011840193832, -6.544527283221437, -1.0987709077226535, -3.3479050964888306,
                      0.030714140514000288, -4.5806106693733],
                     [-3.5928833196381484, 1.014043489632765, 0.3018790199402224, -0.593983963198262,
                      -1.7297184143478108, -3.787745985641347, -3.8789562429866273, -1.5124454321281418,
                      -2.4284262522959823, -2.4410109870407326],
                     [-0.21937297103486664, -2.66168618130091, -0.1766949607779009, -3.174173295372134,
                      -3.00003740568212, -0.4817702757875589, -2.2462888750387444, -1.2268614327018779,
                      -0.44064578384714875, -3.919797023862656], [-2.446710614056073]],
                    AI_TEST_VALUE)

print("Player 2")
for _ in range(100):
    print(play(False, True, myPlayer))

# trialOne = Species(100, 500, 5, 1)
# trialOne.train(10)

# play(False, True, None)


# Loop over, game over
pygame.quit()
