import os
import sys
import collections

sys.path.append('.')
import core.utilities.colour as c
import core.utilities.context as context

class BuilderSeminar(context.BaseBuilder):
    def createArgParser(self):
        super().createArgParser()
        self.parser.add_argument('-c', '--competition', choices = ['FKS', 'KMS', 'UFO', 'KSP', 'Prask', 'FX'])
        self.parser.add_argument('-v', '--volume',      type = int)
        self.parser.add_argument('-s', '--semester',    type = int)
        self.parser.add_argument('-r', '--round',       type = int)

    def path(self):
         

    def createContext(self):
        self.path = (self.args.competition, 
        super().createContext()
    
    def printBuildInfo(self):
        print(c.act("Invoking template builder on"), c.name(self.target),
            c.path("seminar{competition}{volume}{semester}{round}".format(
                competition = '' if self.args.competition    is None else '/{}'.format(self.args.competition),
                volume      = '' if self.args.volume         is None else '/{}'.format(self.args.volume),
                semester    = '' if self.args.semester       is None else '/{}'.format(self.args.semester),
                round       = '' if self.args.round          is None else '/{}'.format(self.args.round),
            ))
        )


class ContextSeminar(context.Context):
    def nodePath(self, root, competition = None, volume = None, semester = None, round = None, problem = None):
        return os.path.join(
            root,
            '' if competition   is None else  competition,
            '' if volume        is None else  '{:02d}'.format(volume),
            '' if semester      is None else  str(semester),
            '' if round         is None else  str(round),
            '' if problem       is None else  '{:02d}'.format(problem),
        )

class ContextModule(ContextSeminar):
    def __init__(self, module):
        super().__init__()
        self.addId(module)

class ContextCompetition(ContextSeminar):
    def __init__(self, root, competition):
        super().__init__()
        self.loadMeta(root, competition).addId(competition)
        
class ContextVolume(ContextSeminar):
    def __init__(self, root, competition, volume):
        super().__init__()
        self.id = '{:02}'.format(volume)
        self.loadMeta(root, competition, volume) \
            .addId(self.id) \
            .addNumber(volume)

class ContextSemester(ContextSeminar):
    def __init__(self, root, competition, volume, semester):
        super().__init__()
        self.id = str(semester)
        self.loadMeta(root, competition, volume, semester) \
            .addId(self.id) \
            .addNumber(semester)
        self.add({
            'nominative':       'zimná' if semester == 1 else 'letná',
            'nominativeNeuter': 'zimné' if semester == 1 else 'letné',
            'genitive':         'zimnej' if semester == 1 else 'letnej',
        })

class ContextSemesterFull(ContextSemester):
    def __init__(self, root, competition, volume, semester):
        super().__init__(root, competition, volume, semester)
        # Missing: fill in rounds and such

class ContextRound(ContextSeminar):
    def __init__(self, root, competition, volume, semester, round):
        super().__init__()
        self.id = str(round)
        self.loadMeta(root, competition, volume, semester, round) \
            .addId(self.id) \
            .addNumber(round)

class ContextRoundFull(ContextRound):
    def __init__(self, root, competition, volume, semester, round):
        super().__init__(root, competition, volume, semester, round)
        
        comp = ContextCompetition(root, competition)
        problems = collections.OrderedDict()

        for p in range(0, len(comp.data['categories'])):
            pn = '{:02d}'.format(p + 1)
            problems[pn] = ContextProblem(root, competition, volume, semester, round, p + 1).data

        self.add({'problems': problems})

class ContextProblem(ContextSeminar):
    def __init__(self, root, competition, volume, semester, round, problem):
        super().__init__()
        self.id = '{:02d}'.format(problem)
        self.loadMeta(root, competition, volume, semester, round, problem) \
            .addId(self.id) \
            .addNumber(problem)

        comp = ContextCompetition(root, competition)
        self.add({'categories': comp.data['categories'][problem - 1]})

class ContextBooklet(ContextSeminar):
    def __init__(self, root, competition, volume, semester, round):
        super().__init__()
        self.absorb('module',           ContextModule       ('seminar'))

        if competition is not None:
            self.absorb('competition',  ContextCompetition  (root, competition))        
        if volume   is not None:
            self.absorb('volume',       ContextVolume       (root, competition, volume))
        if semester is not None:
            self.absorb('semester',     ContextSemester     (root, competition, volume, semester))
        if round    is not None:
            self.absorb('round',        ContextRoundFull    (root, competition, volume, semester, round))
