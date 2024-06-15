# Rhodium

## Disclaimer

This is a personal exploratory project in progress, not production ready code.  

## Introduction

This project is a study in how processing tools and tasks could be managed by a restful micoservice running in a Docker container on behalf of clients that supply that tools and tasks to be managed.

The notion of the service is that tasks will be submitted to the service to be processed by external tools that are tracked by the service.  Tasks have "needs" that express how it is to be processed.  Tools have "skills" that specify what capabilities they have.  A task is matched to a tool for processing according to their respective needs and skills.

An example use case would be a laboratory where instruments periodically collected data that needed to be processed (task) by an appropriate program (tool).  Instruments and their data processing needs would not all be the same.

The service is agnostic of internal details of tool skills and task needs save that they must be valid json.  The actual tool/task assignment is performed by a client-provided assigner that will periodically query the api to get a list of available tasks and tools to consider for assignment.

## Description

The service is written in python and uses fastapi to provide the restful micoservice. It uses  a postgresql database to store its internal state.  SqlModel is used to provide an ORM.  The service container packages the api code, a postgresql database, and a pgadmin instance (as a convenience).

![alt text](diagrams/schema.png)