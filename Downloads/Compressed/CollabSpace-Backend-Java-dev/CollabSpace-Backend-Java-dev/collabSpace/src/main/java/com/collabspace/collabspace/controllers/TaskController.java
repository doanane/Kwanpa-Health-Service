package com.collabspace.collabspace.controllers;

import com.collabspace.collabspace.dto.*;
import com.collabspace.collabspace.enums.TaskStatus;
import com.collabspace.collabspace.services.TaskService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;

@RestController
@RequiredArgsConstructor
@RequestMapping("/tasks")
public class TaskController {

    private final TaskService taskService;

    @PostMapping
    public ResponseEntity<TaskResponseDto> createTask(
            @Valid @RequestBody TaskRequestDto taskRequestDto,
            @RequestHeader("X-User-Id") UUID userId) {

        TaskResponseDto responseDto = taskService.createTask(taskRequestDto, userId);
        return ResponseEntity.status(HttpStatus.CREATED).body(responseDto);
    }

    @GetMapping("/{taskId}")
    public ResponseEntity<TaskResponseDto> getTaskById(@PathVariable UUID taskId) {
        TaskResponseDto responseDto = taskService.getTaskById(taskId);
        return ResponseEntity.ok(responseDto);
    }

    @GetMapping("/project/{projectId}")
    public ResponseEntity<List<TaskResponseDto>> getTasksByProject(@PathVariable UUID projectId) {
        List<TaskResponseDto> tasks = taskService.getAllTasksByProject(projectId);
        return ResponseEntity.ok(tasks);
    }

    @GetMapping("/assignee/{assigneeId}")
    public ResponseEntity<List<TaskResponseDto>> getTasksByAssignee(@PathVariable UUID assigneeId) {
        List<TaskResponseDto> tasks = taskService.getTasksByAssignee(assigneeId);
        return ResponseEntity.ok(tasks);
    }

    @PutMapping("/{taskId}")
    public ResponseEntity<TaskResponseDto> updateTask(
            @PathVariable UUID taskId,
            @Valid @RequestBody TaskRequestDto taskRequestDto,
            @RequestHeader("X-User-Id") UUID userId) {

        TaskResponseDto responseDto = taskService.updateTask(taskId, taskRequestDto, userId);
        return ResponseEntity.ok(responseDto);
    }

    @PatchMapping("/{taskId}/status")
    public ResponseEntity<TaskResponseDto> updateTaskStatus(
            @PathVariable UUID taskId,
            @RequestParam TaskStatus status) {

        TaskResponseDto responseDto = taskService.updateTaskStatus(taskId, status);
        return ResponseEntity.ok(responseDto);
    }

    @DeleteMapping("/{taskId}")
    public ResponseEntity<Void> deleteTask(@PathVariable UUID taskId) {
        taskService.deleteTask(taskId);
        return ResponseEntity.noContent().build();
    }

    @PostMapping("/{taskId}/subtasks")
    public ResponseEntity<SubtaskResponseDto> addSubtask(
            @PathVariable UUID taskId,
            @Valid @RequestBody SubtaskRequestDto subtaskRequestDto) {

        SubtaskResponseDto responseDto = taskService.addSubtask(taskId, subtaskRequestDto);
        return ResponseEntity.status(HttpStatus.CREATED).body(responseDto);
    }

    @GetMapping("/{taskId}/subtasks")
    public ResponseEntity<List<SubtaskResponseDto>> getSubtasksByTask(@PathVariable UUID taskId) {
        List<SubtaskResponseDto> subtasks = taskService.getSubtasksByTask(taskId);
        return ResponseEntity.ok(subtasks);
    }

    @PostMapping("/{taskId}/linked-work-items/{linkedTaskId}")
    public ResponseEntity<TaskResponseDto> addLinkedWorkItem(
            @PathVariable UUID taskId,
            @PathVariable UUID linkedTaskId) {

        TaskResponseDto responseDto = taskService.addLinkedWorkItem(taskId, linkedTaskId);
        return ResponseEntity.ok(responseDto);
    }
}