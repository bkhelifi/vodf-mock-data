# vodf-mock-data

This repository contains scripts to simulate fake data releases to test different VODF format prototypes.

What missing now:
- [ ] ObservationGroupingTable
- [ ] IRFGroupingTable

**Simple Data Release**
No event type, no event class, grouping HDU in the same file than the event and the GTI HDU, the 4 IRFs in an other file

```python do_mock_simple_dr.py```

**Data Release with all event types in the observation**
No event class, grouping HDU in the same file than the event and GTI HDU, the event list has a column with the event types, the IRFs have a flag in their name for each event type

```python do_mock_evttype_dr.py```

**Data Release with one event type per observation**
No event class, one observation is for one event type, and then: grouping HDU in the same file than the filtered event list filtered and the GTI HDU, the 4 IRFs for this given event type in an other file.

```python do_mock_splitted_evttype_dr.py```

