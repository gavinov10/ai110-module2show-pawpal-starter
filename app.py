import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

# Streamlit reruns this whole script on every interaction, so anything
# created with a plain variable is wiped each time. st.session_state acts
# like a dictionary that survives reruns. We create the Owner only if one
# isn't already stored, so its pets and tasks persist as you use the app.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan")

owner: Owner = st.session_state.owner

st.subheader("Owner & Pets")
owner.name = st.text_input("Owner name", value=owner.name)

col_p1, col_p2 = st.columns(2)
with col_p1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col_p2:
    species = st.selectbox("Species", ["dog", "cat", "other"])

# Adding a pet delegates to Owner.add_pet(), which stores a real Pet object
# on the Owner living in session_state — so it survives future reruns.
if st.button("Add pet"):
    owner.add_pet(Pet(name=pet_name, species=species))
    st.success(f"Added {pet_name} ({species}).")

if owner.pets:
    st.write("Current pets:")
    st.table([{"name": p.name, "species": p.species, "tasks": len(p.get_tasks())}
              for p in owner.pets])
else:
    st.info("No pets yet. Add one above.")

st.divider()

st.markdown("### Tasks")
st.caption("Tasks are attached to a pet and feed into the scheduler.")

if not owner.pets:
    st.info("Add a pet first, then you can give it tasks.")
else:
    pet_names = [p.name for p in owner.pets]
    selected_name = st.selectbox("Add task to pet", pet_names)
    selected_pet = next(p for p in owner.pets if p.name == selected_name)

    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    # Adding a task delegates to Pet.add_task(), creating a real Task object.
    if st.button("Add task"):
        selected_pet.add_task(Task(description=task_title, duration=int(duration), priority=priority))
        st.success(f"Added '{task_title}' to {selected_pet.name}.")

    tasks = selected_pet.get_tasks()
    if tasks:
        st.write(f"Tasks for {selected_pet.name}:")
        st.table([{"title": t.description, "duration_minutes": t.duration, "priority": t.priority}
                  for t in tasks])
    else:
        st.info(f"No tasks yet for {selected_pet.name}.")

st.divider()

st.subheader("Build Schedule")
st.caption("Runs the Scheduler over all of the owner's tasks.")

available = st.number_input("Time available today (minutes)", min_value=0, max_value=1440, value=90)

# Generating a schedule delegates to the Scheduler class over the owner's tasks.
if st.button("Generate schedule"):
    owner.set_availability(int(available))
    scheduler = Scheduler.for_owner(owner)
    plan = scheduler.generate_plan()

    if plan:
        st.write("### Today's Schedule")
        for start, task in plan:
            st.write(f"**{start}** — {task.description} ({task.duration} min) · _{task.priority}_")
        st.text(scheduler.explain())
    else:
        st.warning("No tasks could be scheduled. Add tasks or increase available time.")
