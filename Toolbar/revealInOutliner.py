try:
    reload(revealInOutliner)
    revealInOutliner.run()

except NameError:
    import revealInOutliner
    revealInOutliner.run()