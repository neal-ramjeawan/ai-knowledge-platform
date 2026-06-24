# AI Knowledge Platform

A local-first document ingestion and retrieval API built with FastAPI, PostgreSQL, pgvector, and Docker Compose.

## Current Features

- Upload text documents
- Store document metadata and content in PostgreSQL
- Split documents into searchable chunks
- Search chunks using PostgreSQL full-text search
- Ask questions and retrieve relevant context
- Run the API and database with Docker Compose
- Apply database schema using a versioned SQL migration
- Use a Makefile for repeatable local development commands
- Generate local embeddings for document chunks
- Store embeddings in pgvector
- Search chunks using semantic vector similarity

## Tech Stack

- Python 3.14
- FastAPI
- PostgreSQL 17
- pgvector
- Docker
- Colima
- Docker Compose
- Makefile

## Architecture

Client / Swagger UI
        |
        v
FastAPI API Container
        |
        v
PostgreSQL + pgvector Container