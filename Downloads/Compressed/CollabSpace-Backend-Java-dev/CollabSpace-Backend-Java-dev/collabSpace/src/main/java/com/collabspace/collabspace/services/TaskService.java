package com.collabspace.collabspace.services;

import com.collabspace.collabspace.dto.*;
import com.collabspace.collabspace.entity.Project;
import com.collabspace.collabspace.entity.Task;
import com.collabspace.collabspace.entity.Subtask;
import com.collabspace.collabspace.enums.TaskStatus;
import com.collabspace.collabspace.repository.ProjectRepository;
import com.collabspace.collabspace.repository.TaskRepository;
import com.collabspace.collabspace.repository.SubtaskRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class TaskService {

    private final TaskRepository taskRepository;
    private final SubtaskRepository subtaskRepository;
    private final ProjectRepository projectRepository;

    @Transactional
    public TaskResponseDto createTask(TaskRequestDto taskRequestDto, UUID userId) {
        Project project = projectRepository.findById(taskRequestDto.getProjectId())
                .orElseThrow(() -> new RuntimeException("Project not found"));

        Task task = new Task();
        task.setTitle(taskRequestDto.getTitle());
        task.setDescription(taskRequestDto.getDescription());
        task.setProject(project);
        task.setAssigneeId(taskRequestDto.getAssigneeId());
        task.setDueDate(taskRequestDto.getDueDate());
        task.setPriority(taskRequestDto.getPriority());
        task.setStatus(TaskStatus.TO_DO);

        Task savedTask = taskRepository.save(task);
        return convertToTaskResponseDto(savedTask);
    }

    public TaskResponseDto getTaskById(UUID taskId) {
        Task task = taskRepository.findById(taskId)
                .orElseThrow(() -> new RuntimeException("Task not found"));
        return convertToTaskResponseDto(task);
    }

    public List<TaskResponseDto> getAllTasksByProject(UUID projectId) {
        List<Task> tasks = taskRepository.findByProjectId(projectId);
        return tasks.stream()
                .map(this::convertToTaskResponseDto)
                .collect(Collectors.toList());
    }

    public List<TaskResponseDto> getTasksByAssignee(UUID assigneeId) {
        List<Task> tasks = taskRepository.findByAssigneeId(assigneeId);
        return tasks.stream()
                .map(this::convertToTaskResponseDto)
                .collect(Collectors.toList());
    }

    @Transactional
    public TaskResponseDto updateTask(UUID taskId, TaskRequestDto taskRequestDto, UUID userId) {
        Task task = taskRepository.findById(taskId)
                .orElseThrow(() -> new RuntimeException("Task not found"));

        if (taskRequestDto.getTitle() != null) {
            task.setTitle(taskRequestDto.getTitle());
        }
        if (taskRequestDto.getDescription() != null) {
            task.setDescription(taskRequestDto.getDescription());
        }
        if (taskRequestDto.getAssigneeId() != null) {
            task.setAssigneeId(taskRequestDto.getAssigneeId());
        }
        if (taskRequestDto.getDueDate() != null) {
            task.setDueDate(taskRequestDto.getDueDate());
        }
        if (taskRequestDto.getPriority() != null) {
            task.setPriority(taskRequestDto.getPriority());
        }

        Task updatedTask = taskRepository.save(task);
        return convertToTaskResponseDto(updatedTask);
    }

    @Transactional
    public TaskResponseDto updateTaskStatus(UUID taskId, TaskStatus status) {
        Task task = taskRepository.findById(taskId)
                .orElseThrow(() -> new RuntimeException("Task not found"));

        task.setStatus(status);
        Task updatedTask = taskRepository.save(task);
        return convertToTaskResponseDto(updatedTask);
    }

    @Transactional
    public void deleteTask(UUID taskId) {
        Task task = taskRepository.findById(taskId)
                .orElseThrow(() -> new RuntimeException("Task not found"));
        taskRepository.delete(task);
    }

    @Transactional
    public SubtaskResponseDto addSubtask(UUID taskId, SubtaskRequestDto subtaskRequestDto) {
        Task parentTask = taskRepository.findById(taskId)
                .orElseThrow(() -> new RuntimeException("Parent task not found"));

        Subtask subtask = new Subtask();
        subtask.setTitle(subtaskRequestDto.getTitle());
        subtask.setDescription(subtaskRequestDto.getDescription());
        subtask.setParentTask(parentTask);
        subtask.setAssigneeId(subtaskRequestDto.getAssigneeId());
        subtask.setStatus(TaskStatus.TO_DO);

        Subtask savedSubtask = subtaskRepository.save(subtask);
        return convertToSubtaskResponseDto(savedSubtask);
    }

    @Transactional
    public TaskResponseDto addLinkedWorkItem(UUID taskId, UUID linkedTaskId) {
        Task task = taskRepository.findById(taskId)
                .orElseThrow(() -> new RuntimeException("Task not found"));

        Task linkedTask = taskRepository.findById(linkedTaskId)
                .orElseThrow(() -> new RuntimeException("Linked task not found"));

        if (!task.getLinkedWorkItems().contains(linkedTask)) {
            task.getLinkedWorkItems().add(linkedTask);
        }

        Task updatedTask = taskRepository.save(task);
        return convertToTaskResponseDto(updatedTask);
    }

    public List<SubtaskResponseDto> getSubtasksByTask(UUID taskId) {
        List<Subtask> subtasks = subtaskRepository.findByParentTaskId(taskId);
        return subtasks.stream()
                .map(this::convertToSubtaskResponseDto)
                .collect(Collectors.toList());
    }

    private TaskResponseDto convertToTaskResponseDto(Task task) {
        TaskResponseDto responseDto = new TaskResponseDto();
        responseDto.setId(task.getId());
        responseDto.setTitle(task.getTitle());
        responseDto.setDescription(task.getDescription());
        responseDto.setProjectId(task.getProject().getId());
        responseDto.setProjectName(task.getProject().getName());
        responseDto.setAssigneeId(task.getAssigneeId());
        responseDto.setStatus(task.getStatus());
        responseDto.setPriority(task.getPriority());
        responseDto.setDueDate(task.getDueDate());
        responseDto.setCreatedAt(task.getCreationAt());

        // Convert subtasks
        List<SubtaskResponseDto> subtaskDtos = subtaskRepository.findByParentTaskId(task.getId())
                .stream()
                .map(this::convertToSubtaskResponseDto)
                .collect(Collectors.toList());
        responseDto.setSubtasks(subtaskDtos);

        // Convert linked work items
        if (task.getLinkedWorkItems() != null) {
            List<TaskLinkDto> linkedWorkItemDtos = task.getLinkedWorkItems().stream()
                    .map(linkedTask -> {
                        TaskLinkDto linkDto = new TaskLinkDto();
                        linkDto.setId(linkedTask.getId());
                        linkDto.setTitle(linkedTask.getTitle());
                        linkDto.setStatus(linkedTask.getStatus().name());
                        return linkDto;
                    })
                    .collect(Collectors.toList());
            responseDto.setLinkedWorkItems(linkedWorkItemDtos);
        }

        return responseDto;
    }

    private SubtaskResponseDto convertToSubtaskResponseDto(Subtask subtask) {
        SubtaskResponseDto responseDto = new SubtaskResponseDto();
        responseDto.setId(subtask.getId());
        responseDto.setTitle(subtask.getTitle());
        responseDto.setDescription(subtask.getDescription());
        responseDto.setParentTaskId(subtask.getParentTask().getId());
        responseDto.setAssigneeId(subtask.getAssigneeId());
        responseDto.setStatus(subtask.getStatus());
        responseDto.setCreatedAt(subtask.getCreatedAt());
        return responseDto;
    }
}