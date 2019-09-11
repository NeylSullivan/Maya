def GetRangePct(MinValue, MaxValue, Value):
    # Avoid Divide by Zero. But also if our range is a point, output whether Value is before or after.
    Divisor = MaxValue - MinValue
    if abs(Divisor) < 0.00001:
        return 1.0 if Value >= MaxValue else 0.0
    return (Value - MinValue) / Divisor

def LerpStable(A, B, Alpha):
    return (A * (1.0 - Alpha)) + (B * Alpha)

def Clamp(X, Min, Max):
    if X < Min:
        return Min
    elif X > Max:
        return Max
    return X

def Clamp01(X):
    return Clamp(X, 0.0, 1.0)

def MapRangeUnclamped(Value, InRangeA, InRangeB, OutRangeA, OutRangeB):
    return LerpStable(OutRangeA, OutRangeB, GetRangePct(InRangeA, InRangeB, Value))

def MapRangeClamped(Value, InRangeA, InRangeB, OutRangeA, OutRangeB):
    return LerpStable(OutRangeA, OutRangeB, Clamp01(GetRangePct(InRangeA, InRangeB, Value)))
