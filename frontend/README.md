# Future Self Advisor

Create a premium, high-tech, responsive React/Tailwind web app for "Digital Twin AI" — a personal decision-support dashboard that simulates future life outcomes (finances, habits, study/work focus) using predictive analytics and LLM advisors.

Here is the structural mapping of the exact buttons and text labels required on each screen to make the application fully functional:

---

Screen 1: Onboarding & Auth (The Sync Screen)

*   Button 1: `Create Twin Profile`

       Action*: Saves the user input details (age, target age, base income, net worth goals) to initialize the database profile and enters the Dashboard.

*   Button 2: `Load Demo Twin`

       Action*: Bypasses form entry and seeds the database with a pre-configured 30-day history (representing test user Alice) to immediately show the dashboard.

---

Screen 2: Dashboard Overview (Twin Core)

*   Button 1: `Log Daily Habits`

       Action*: Opens the sliding sidebar drawer to input sleep hours, screen time, socializing, and study logs.

*   Button 2: `Record Transaction`

       Action*: Opens a modal dialog to log a new income or expense transaction.

*   Button 3: `Optimize Routine`

       Action*: Redirects the user directly to the What-If Simulator screen.

*   Button 4: `Refresh Twin Status`

       Action*: Forces a recalculation of the user's 30-day baseline statistics from the database.

---

Screen 3: What-If Sandbox (Decision Simulator)

*   Button 1: `Run Comparative Analysis`

       Action*: Computes Net Worth projections and lifestyle ratings side-by-side for both Scenario A and Scenario B.

*   Button 2: `Adopt Scenario A`

       Action*: Saves Scenario A values as the user's new active profile metrics.

*   Button 3: `Adopt Scenario B`

       Action*: Saves Scenario B values as the user's new active profile metrics.

*   Button 4: `Reset Sandbox`

       Action*: Returns all sliders (savings rate, sleep, study time) back to the user's default baseline values.

---

Screen 4: Financial Forecast (Wealth Planner)

*   Button 1: `Run Monte Carlo Model`

       Action*: Triggers 500 stochastic iterations of asset compounding and renders the probability band curves.

*   Button 2: `Show Deterministic Path`

       Action*: Switches the visual chart view to a standard compound interest line chart.

*   Button 3: `Update Targets`

       Action*: Saves modifications to the retirement target values (Target Age, Target Net Worth).

---

Screen 5: Habits & Performance Analytics

*   Button 1: `Submit Log`

       Action*: Validates the habit inputs and commits them to the database.

*   Button 2: `Cancel Log`

       Action*: Closes the log entry drawer without saving.

*   Button 3: `Export History (CSV)`

       Action*: Downloads the historical table data of habit logs as a CSV file.

*   Button 4: `Clear All Logs`

       Action*: Deletes the user's habit history from the database (destructive action).

SHADOW & GLOW STATES (CSS SPECIFICATION)
- Active radial gauges and cards must use subtle neon glows:
  - Cyan elements: `shadow-[0_0_15px_rgba(102,252,241,0.2)]`
  - Purple elements: `shadow-[0_0_15px_rgba(138,43,226,0.2)]`
- Add a custom `@keyframes pulse-glow` animation for calculation states:
  - While sliders are being dragged or a simulation is running, animate the shadow blur of the dials and charts from 10px (low intensity) to 25px (high intensity) at 1.5s intervals.

DYNAMIC GLOW STATES FLOW
1. RESTING STATE: Dials emit a soft, steady ambient glow.
2. INPUT STATE: When a user drags a simulator slider, the active slider thumb glows with cyan light, and the charts show a temporary pulse glow animation representing "Syncing Twin Forecast".
3. OUTCOME EVALUATION STATE:
   - If the simulated outcome reaches the financial target successfully, trigger a brief 0.5s glowing emerald checkmark/burst on the success metric.
   - If a slider combination drops the projected Sleep Index or Health Index below 5.0, immediately shift the glow color of that panel from Cyan to Warning Crimson (glowing red warning state) to notify the user of burnout risk.

DESIGN SYSTEM & AESTHETICS (Must be visually stunning)

- Theme: Deep cyber dark mode. 

- Colors: Background `#0B0C10` (almost black), secondary panels in dark slate grey `#1F2833` with semi-transparent glassmorphism (glass card backgrounds, thin border of `rgba(255,255,255,0.08)`, backdrop blur).

- Accent Colors: Neon Cyan (`#66FCF1`), Electric Purple (`#8A2BE2`), and Emerald Green (`#00E676`).







- Fonts: Outfit (headings), Inter (body). 

- Details: Smooth transitions on hovers, glowing drop shadows for active dials, clean neon lines, and absolute premium UI aesthetics. Do not use generic tailwind colors; use cohesive modern HSL/RGB colors.

CORE NAVIGATION & LAYOUT

- Include a sleek, collapsible sidebar on the left with glowing active states and icons:

  1. Dashboard Overview (Twin Core)

  2. What-If Simulator (Decision Sandbox)

  3. Wealth Planner (Financial Twin)

  4. Habits & Analytics

  5. Profile & Goals

- Top header displaying the active user profile (e.g., "Alice - Sync Status: Online") and a notification bell.

SCREEN 1: DASHBOARD OVERVIEW (Twin Core)

- Two large radial gauge dials (using Recharts or SVG gradients) showing:

  - "Health & Vitality Index" (7.6/10) - Cyan gradient

  - "Cognitive Focus Index" (8.2/10) - Purple gradient

- "Twin Status Feed": An elegant card presenting AI-generated insights (e.g., "Your screen time yesterday was 2.5 hours above baseline. Focus prediction is down 4%. Recommended action: sleep 30 mins more tonight.")

- Quick stats grid showing Current Net Worth ($25,420), Daily Sleep (7.5h), Weekly Study Hours (8.5h) with neon accent icons.

- A mini chart showing the user's progress toward their primary goal (e.g., "Emergency Fund: $15k/$20k").

SCREEN 2: WHAT-IF SIMULATOR (Decision Sandbox)

- A comparative split-screen layout.

- Left column (Adjust Scenario A vs B):

  - Sliders for Scenario A: Monthly Savings Change ($0 to +$2000), Sleep Change (-2h to +3h), Weekly Study Change (-10h to +20h).

  - Sliders for Scenario B: Same inputs.

- Center/Right column:

  - "Future Trajectory Comparison Chart": A clean double-axis line chart (using Recharts). One axis plots Net Worth over 5 years (Scenario A vs B), the other axis plots projected Focus Score.

  - "Digital Twin Advisor Verdict Panel": A glowing card styled like an AI terminal message output. Display a formatted report analyzing tradeoffs, comparing health indicators, and declaring a clear "Verdict Recommendation".

SCREEN 3: WEALTH PLANNER (Financial Twin)

- A financial calculator layout where users see their target retirement net worth (e.g. $1,000,000) and age (e.g. 60).

- Interactive Monte Carlo Simulation chart: Shows three paths (90th percentile optimistic, 50th percentile median, 10th percentile pessimistic) of asset growth over time.

- Success Probability gauge: Displays a radial dial showing "Probability of Success: 82%".

- An dynamic budgeting card showing monthly income vs. fixed/discretionary expenses.

SCREEN 4: HABITS & PERFORMANCE ANALYTICS

- A form overlay or slide-out drawer to "Log Daily Activities" (Log Sleep, Log Exercise, Log Expenses, Log Study session details including exam scores).

- A grid of correlation heatmaps or bubble charts showing lifestyle dependencies (e.g., Sleep hours vs. Focus rating).

- A weekly calendar tracker showing habits streaks in glowing green checkboxes.

STATE MANAGEMENT & SAMPLE DATA

- Seed the UI with a complete set of mock data so it looks fully functional. 

- Toggling the What-If sliders should dynamically recalculate values (e.g., shifting the savings slider up should increase the terminal net worth on the line chart; reducing sleep should drop the Health Index radial score).

- Support logging custom habit transactions that update the dashboard metrics locally.


So the project flow is firstly, we have a signup page a login page and firstly use a sign. Then you have to create a settings in which we store the main database in which will ask for the basic things like yearly income on monthly income, like normal habits or hobbies. Something related to the project. I am making simple questions. Questions should be like like a slider so it will be like if you ask another question, it will just slide from the right to left and it will go to the next question after completing that all things will be stored in the settings. Now people can retriever change the settings. Also, you have to make a dialogue available in every kind of page so that basically you can change the setting time you can you want now. Basically, you have to make the side in such a way like everything is sorted in simple words, like not like habits. Instead, you should think word like task goal and we have to make a inbuilt daily planet system. So basically it will make a plan for today's and it will make a timetable as of your choice, so you have to basically make two systems like first will be for your timetable or habit and other other one will be where you'll get suggestions right where I'll get suggestions what you can implement, and if the person implement the thing will be shown in the task so that they can use that thing in the task list. The task is very simple. You can make a simple task applications, but you have to integrate like with the with the recommendation system so that it doesn't get mixed and you have to make both UI dark and lighting so that people can change basic of their base of their choices. After completing all the choices, make the UI come back modernised and not give me look. I don't want any look. I want to simply look like simply dia with using white black as a primary colours. That's it.

This project was built with [Lovable](https://lovable.dev).

**Live app**: https://twin-path-navigator.lovable.app

## Build with Lovable

Continue developing this project in the [Lovable editor](https://lovable.dev/projects/1c0d925f-a14f-4510-84c1-b304227392f2).

- **Ship faster**: describe what you want to build and Lovable handles the code.
- **Stay in sync**: every change made in Lovable is committed straight to this repository.
- **Full ownership**: this code is yours. Push to `main` on GitHub and your changes sync back into Lovable, ready for your next prompt.

## Development

Prefer working locally? You need Node.js and npm — [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating).

```sh
git clone <this-repository-url>
cd <repository-name>
npm i
npm run dev
```
