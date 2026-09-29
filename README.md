<h1 align="center">Hey, I'm Mohit <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Hand%20gestures/Waving%20Hand.png" alt="👋" width="36" height="36" /></h1>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=500&size=20&duration=3200&pause=1000&color=C9D1D9&center=true&vCenter=true&width=620&lines=Software+Engineer+%C2%B7+2%2B+yrs+shipping+to+production;Serverless+%26+event-driven+backends+on+AWS;iOS+%26+Android+in-app+payments%2C+end+to+end;RL+environments+for+AI+coding+agents" />
    <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=500&size=20&duration=3200&pause=1000&color=57606A&center=true&vCenter=true&width=620&lines=Software+Engineer+%C2%B7+2%2B+yrs+shipping+to+production;Serverless+%26+event-driven+backends+on+AWS;iOS+%26+Android+in-app+payments%2C+end+to+end;RL+environments+for+AI+coding+agents" alt="Software Engineer · serverless and event-driven backends on AWS · iOS and Android in-app payments · RL environments for AI coding agents" />
  </picture>
</p>

<p align="center">
  <a href="https://www.linkedin.com/in/mohit-pal-b0076a185/" title="Connect on LinkedIn"><img src="https://img.shields.io/badge/LinkedIn-24292F?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn" /></a>
  <a href="mailto:mohitpal2621@gmail.com" title="mohitpal2621@gmail.com"><img src="https://img.shields.io/badge/Email-24292F?style=for-the-badge&logo=gmail&logoColor=white" alt="Email" /></a>
  <a href="https://leetcode.com/u/mohitpal2621/" title="340+ problems solved"><img src="https://img.shields.io/badge/LeetCode-340%2B%20solved-24292F?style=for-the-badge&logo=leetcode&logoColor=white&labelColor=24292F" alt="LeetCode: 340+ problems solved" /></a>
</p>

<p align="center">
  <a href="#about-me" title="Jump to About"><kbd>&nbsp;About&nbsp;</kbd></a>&nbsp;
  <a href="#what-ive-shipped" title="Jump to Experience"><kbd>&nbsp;Experience&nbsp;</kbd></a>&nbsp;
  <a href="#how-i-build" title="Jump to How I build"><kbd>&nbsp;How I build&nbsp;</kbd></a>&nbsp;
  <a href="#tech-stack" title="Jump to Stack"><kbd>&nbsp;Stack&nbsp;</kbd></a>&nbsp;
  <a href="#featured-projects" title="Jump to Projects"><kbd>&nbsp;Projects&nbsp;</kbd></a>&nbsp;
  <a href="#lets-connect" title="Jump to Contact"><kbd>&nbsp;Contact&nbsp;</kbd></a>
</p>

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/People/Man%20Technologist.png" alt="🧑‍💻" width="28" height="28" /> About me

I'm a backend-leaning **full-stack Software Engineer** with **2+ years** of shipping production systems. I design **serverless, event-driven services on AWS**, own features **end to end across web and mobile**, and build **RL environments and verifiers for AI coding agents**.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/mohitpal2621/mohitpal2621/main/assets/terminal-dark.svg" />
    <img src="https://raw.githubusercontent.com/mohitpal2621/mohitpal2621/main/assets/terminal-light.svg" alt="Animated terminal. whoami: Mohit Pal, Software Engineer, Gurgaon, India. focus: serverless, event-driven backends on AWS; iOS and Android in-app payments; RL environments and verifiers for AI coding agents. stack: node, nestjs, typescript, python, lambda, dynamodb, eventbridge, sqs, react-native" width="100%" />
  </picture>
</p>

- 🔭 **Now:** Software Engineer at **4 Way Technologies**, building **SpicyChat** and **PixelChat** for NextDay AI
- 🤖 **Also:** contract work with **Handshake AI** on agentic coding tasks and RL environments in Python
- 🎓 **Education:** B.Tech CSE, Maharaja Agrasen Institute of Technology, Delhi (2024) · CGPA 8.7
- 📍 **Based in:** Gurgaon, India

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Travel%20and%20places/Rocket.png" alt="🚀" width="28" height="28" /> What I've shipped

<details open>
<summary><b>🏢 Software Engineer · 4 Way Technologies</b> &nbsp;<sub>Aug 2024 – Present · New Delhi, India</sub></summary>
<br />

**NextDay AI: SpicyChat & PixelChat** · high-traffic AI chat platforms
- Own backend **and** frontend end to end with Node.js, TypeScript, React and React Native
- Designed serverless microservices on **AWS Lambda, API Gateway and DynamoDB**, shipped with the Serverless Framework across dev → UAT → prod
- Built event-driven workflows on **EventBridge, SQS and Step Functions** for async and background processing
- Extended the **Contentful + GraphQL** integration to serve platform-specific premium content without app releases

**ChatReal AI**
- Implemented **iOS & Android in-app purchases and subscriptions** end to end with react-native-iap and server-side receipt validation
- Processed subscription lifecycle events in real time with **Google Cloud Pub/Sub**
- Built modular **NestJS** REST APIs with rate limiting on chat and LLM endpoints

</details>

<details open>
<summary><b>🤖 Handshake AI · Contract</b> &nbsp;<sub>RL environments & agentic coding tasks</sub></summary>
<br />

- Author Dockerized coding tasks with **verifiers and trial harnesses** in Python, used to train and evaluate AI coding agents
- **30+ accepted tasks** across Handshake AI and other RL data platforms, spanning security, ML, data/ETL, debugging and scientific computing
- Built my own tooling for the work, including a task validation toolchain and a CI monitoring dashboard

</details>

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Travel%20and%20places/High%20Voltage.png" alt="⚡" width="28" height="28" /> How I build

A typical serverless, event-driven flow I design and ship, simplified. Hover the diagram for zoom and pan controls.

```mermaid
flowchart TB
    subgraph SUBS["💳 Subscriptions"]
        direction LR
        stores["🛒 App Store & Google Play"] -->|receipts & lifecycle events| pubsub["GCP Pub/Sub"]
    end
    subgraph REQ["⚡ Request path"]
        direction LR
        client["📱 Mobile & web apps"] -->|HTTPS| apigw["API Gateway"] --> fn["λ Lambda · Node.js / TypeScript"] --> ddb[("DynamoDB")]
    end
    subgraph ASYNC["🔁 Event-driven background work"]
        direction LR
        bus{{"EventBridge"}} --> queue["SQS"] --> workers["λ Worker Lambdas"] --> flow["Step Functions"]
    end
    SUBS -->|validated server-side| REQ
    REQ -->|domain events| ASYNC
```

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Hammer%20and%20Wrench.png" alt="🛠️" width="28" height="28" /> Tech stack

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/mohitpal2621/mohitpal2621/main/assets/stack-ticker-dark.svg" />
    <img src="https://raw.githubusercontent.com/mohitpal2621/mohitpal2621/main/assets/stack-ticker-light.svg" alt="Tech I work with: AWS Lambda, API Gateway, DynamoDB, EventBridge, SQS, Step Functions, S3, Serverless Framework, GCP Pub/Sub, Cloudflare, Docker, GitHub Actions, TypeScript, Node.js, NestJS, Python, React Native, React, Next.js, GraphQL, Socket.IO, MongoDB, Prisma, Contentful, LangChain, Jest" width="100%" />
  </picture>
</p>

| Area | Tools |
| :-- | :-- |
| **Languages** | ![TypeScript](https://img.shields.io/badge/TypeScript-24292F?style=flat-square&logo=typescript&logoColor=white) ![JavaScript](https://img.shields.io/badge/JavaScript-24292F?style=flat-square&logo=javascript&logoColor=white) ![Python](https://img.shields.io/badge/Python-24292F?style=flat-square&logo=python&logoColor=white) ![C++](https://img.shields.io/badge/C%2B%2B-24292F?style=flat-square&logo=cplusplus&logoColor=white) ![SQL](https://img.shields.io/badge/SQL-24292F?style=flat-square) |
| **Backend** | ![Node.js](https://img.shields.io/badge/Node.js-24292F?style=flat-square&logo=nodedotjs&logoColor=white) ![NestJS](https://img.shields.io/badge/NestJS-24292F?style=flat-square&logo=nestjs&logoColor=white) ![Express](https://img.shields.io/badge/Express-24292F?style=flat-square&logo=express&logoColor=white) ![REST APIs](https://img.shields.io/badge/REST%20APIs-24292F?style=flat-square) ![GraphQL](https://img.shields.io/badge/GraphQL-24292F?style=flat-square&logo=graphql&logoColor=white) ![Socket.IO](https://img.shields.io/badge/Socket.IO-24292F?style=flat-square&logo=socketdotio&logoColor=white) |
| **Cloud & Serverless** | ![AWS Lambda](https://img.shields.io/badge/AWS%20Lambda-24292F?style=flat-square) ![API Gateway](https://img.shields.io/badge/API%20Gateway-24292F?style=flat-square) ![DynamoDB](https://img.shields.io/badge/DynamoDB-24292F?style=flat-square) ![EventBridge](https://img.shields.io/badge/EventBridge-24292F?style=flat-square) ![SQS](https://img.shields.io/badge/SQS-24292F?style=flat-square) ![Step Functions](https://img.shields.io/badge/Step%20Functions-24292F?style=flat-square) ![S3](https://img.shields.io/badge/S3-24292F?style=flat-square) ![Serverless Framework](https://img.shields.io/badge/Serverless%20Framework-24292F?style=flat-square&logo=serverless&logoColor=white) ![GCP Pub/Sub](https://img.shields.io/badge/GCP%20Pub%2FSub-24292F?style=flat-square&logo=googlepubsub&logoColor=white) ![Cloudflare](https://img.shields.io/badge/Cloudflare-24292F?style=flat-square&logo=cloudflare&logoColor=white) |
| **Web & Mobile** | ![React](https://img.shields.io/badge/React-24292F?style=flat-square&logo=react&logoColor=white) ![React Native](https://img.shields.io/badge/React%20Native-24292F?style=flat-square&logo=react&logoColor=white) ![Next.js](https://img.shields.io/badge/Next.js-24292F?style=flat-square&logo=nextdotjs&logoColor=white) ![Redux](https://img.shields.io/badge/Redux-24292F?style=flat-square&logo=redux&logoColor=white) ![App Store IAP](https://img.shields.io/badge/App%20Store%20IAP-24292F?style=flat-square&logo=appstore&logoColor=white) ![Google Play Billing](https://img.shields.io/badge/Google%20Play%20Billing-24292F?style=flat-square&logo=googleplay&logoColor=white) |
| **Data & CMS** | ![MongoDB](https://img.shields.io/badge/MongoDB-24292F?style=flat-square&logo=mongodb&logoColor=white) ![MySQL](https://img.shields.io/badge/MySQL-24292F?style=flat-square&logo=mysql&logoColor=white) ![Prisma](https://img.shields.io/badge/Prisma-24292F?style=flat-square&logo=prisma&logoColor=white) ![TypeORM](https://img.shields.io/badge/TypeORM-24292F?style=flat-square&logo=typeorm&logoColor=white) ![Firebase](https://img.shields.io/badge/Firebase-24292F?style=flat-square&logo=firebase&logoColor=white) ![Contentful](https://img.shields.io/badge/Contentful-24292F?style=flat-square&logo=contentful&logoColor=white) |
| **AI & DevOps** | ![LangChain](https://img.shields.io/badge/LangChain-24292F?style=flat-square&logo=langchain&logoColor=white) ![LLM apps](https://img.shields.io/badge/LLM%20apps-24292F?style=flat-square) ![RL environments](https://img.shields.io/badge/RL%20environments-24292F?style=flat-square) ![Docker](https://img.shields.io/badge/Docker-24292F?style=flat-square&logo=docker&logoColor=white) ![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-24292F?style=flat-square&logo=githubactions&logoColor=white) ![Jest](https://img.shields.io/badge/Jest-24292F?style=flat-square&logo=jest&logoColor=white) ![Linux](https://img.shields.io/badge/Linux-24292F?style=flat-square&logo=linux&logoColor=white) ![Git](https://img.shields.io/badge/Git-24292F?style=flat-square&logo=git&logoColor=white) ![Postman](https://img.shields.io/badge/Postman-24292F?style=flat-square&logo=postman&logoColor=white) |

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Travel%20and%20places/Fire.png" alt="🔥" width="28" height="28" /> Featured projects

<table>
  <tr>
    <td width="50%" valign="top">
      <h3><a href="https://github.com/mohitpal2621/realTimeChatApp">💬 Chat-Pulse</a></h3>
      Real-time chat app with JWT auth, 1:1 and group chats, typing indicators, unread counts and read receipts.
      <br /><br />
      <code>React</code> <code>Chakra UI</code> <code>Node.js</code> <code>Express</code> <code>Socket.IO</code> <code>MongoDB</code>
    </td>
    <td width="50%" valign="top">
      <h3><a href="https://github.com/mohitpal2621/Nest-js">🚗 Car Pricing API</a></h3>
      NestJS API that estimates used-car prices from approved sale reports, with cookie-session auth, scrypt password hashing, admin guards and e2e tests.
      <br /><br />
      <code>NestJS</code> <code>TypeScript</code> <code>TypeORM</code> <code>SQLite</code> <code>Jest</code>
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <h3><a href="https://github.com/mohitpal2621/BlogPulse">📝 BlogPulse</a></h3>
      Markdown-powered blog on Next.js with static generation and incremental revalidation, syntax-highlighted posts and a MongoDB-backed contact API.
      <br /><br />
      <code>Next.js</code> <code>React</code> <code>MongoDB</code> <code>Markdown</code>
    </td>
    <td width="50%" valign="top">
      <h3><a href="https://github.com/mohitpal2621/Expensify">💸 Expensify</a></h3>
      Expense manager with Google sign-in, Firebase sync, date-range filters and sorting, a Jest test suite and a custom Webpack build.
      <br /><br />
      <code>React</code> <code>Redux</code> <code>Firebase</code> <code>Jest</code> <code>Webpack</code>
    </td>
  </tr>
</table>

<details>
<summary><b>📂 More projects</b> (click to expand)</summary>
<br />

| Project | What it is | Stack |
| :-- | :-- | :-- |
| [DSA](https://github.com/mohitpal2621/DSA) | Data structures and algorithms practice: linked lists, priority queues and sorting | C++ |
| [KeeperNotes](https://github.com/mohitpal2621/KeeperNotes) | Notes app with a Material UI front end and an Express + MongoDB API | React, MUI, Express, Mongoose |
| [dashboard](https://github.com/mohitpal2621/dashboard) | Data dashboard with filterable views served from an Express + MongoDB API | React, Express, Mongoose |
| [code-detective-be](https://github.com/mohitpal2621/code-detective-be) | NestJS + Prisma backend, work in progress | NestJS, Prisma, TypeScript |

</details>

> [!NOTE]
> Most of my production work lives in private client repositories. Happy to walk through the architecture in a conversation.

<details>
<summary><b>🐍 Psst, click to watch a snake eat my contribution graph</b></summary>
<br />
<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/mohitpal2621/mohitpal2621/output/github-snake-dark.svg" />
    <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/mohitpal2621/mohitpal2621/output/github-snake.svg" />
    <img alt="Snake eating my GitHub contribution graph" src="https://raw.githubusercontent.com/mohitpal2621/mohitpal2621/output/github-snake.svg" />
  </picture>
</p>
</details>

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Hand%20gestures/Handshake.png" alt="🤝" width="28" height="28" /> Let's connect

Always happy to talk serverless architecture, in-app payments or AI tooling.

<p align="center">
  <a href="https://www.linkedin.com/in/mohit-pal-b0076a185/" title="Connect on LinkedIn"><img src="https://img.shields.io/badge/LinkedIn-Say%20hi-24292F?style=for-the-badge&logo=linkedin&logoColor=white&labelColor=24292F" alt="LinkedIn" /></a>
  <a href="mailto:mohitpal2621@gmail.com" title="mohitpal2621@gmail.com"><img src="https://img.shields.io/badge/Email-Drop%20a%20line-24292F?style=for-the-badge&logo=gmail&logoColor=white&labelColor=24292F" alt="Email" /></a>
</p>

<p align="center">
  <img src="https://komarev.com/ghpvc/?username=mohitpal2621&label=Profile%20views&color=24292F&style=flat-square" alt="Profile views" />
  <br />
  <sub><a href="#hey-im-mohit">Back to top ↑</a></sub>
</p>
