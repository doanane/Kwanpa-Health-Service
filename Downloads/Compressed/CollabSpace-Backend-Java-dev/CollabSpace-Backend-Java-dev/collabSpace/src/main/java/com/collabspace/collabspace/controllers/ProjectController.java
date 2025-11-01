package com.collabspace.collabspace.controllers;

import com.collabspace.collabspace.dto.ProjectRequestDto;
import com.collabspace.collabspace.dto.ProjectResponseDto;
import com.collabspace.collabspace.services.ProjectService;
import jakarta.validation.Valid;
import lombok.AllArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;
import java.util.UUID;

@RestController
@AllArgsConstructor
@RequestMapping("/projects")
public class ProjectController {
    private final ProjectService projectService;


    @PostMapping
    public ResponseEntity<ProjectResponseDto>  createProject(@Valid @RequestBody ProjectRequestDto projectDto,
                        @RequestHeader("X-User-Id") UUID userId)
     {
        ProjectResponseDto responseDto = projectService.createProject(projectDto, userId);
        return ResponseEntity.status(HttpStatus.CREATED).body(responseDto);
    }

    @GetMapping("/{projectId}")
    public ResponseEntity<ProjectResponseDto> getProjectById(@PathVariable UUID projectId){
        ProjectResponseDto projectResponseDto = projectService.getProjectById(projectId);
        return ResponseEntity.ok(projectResponseDto);
    }

    @PutMapping("/{projectId}")
    public ResponseEntity<ProjectResponseDto>  updateProject(@Valid @PathVariable UUID projectId, @RequestBody ProjectRequestDto projectDto,
                                                             @RequestHeader("X-User-Id") UUID userId)
    {
        ProjectResponseDto responseDto = projectService.updateProject(projectId,projectDto, userId);
        return ResponseEntity.status(HttpStatus.CREATED).body(responseDto);
    }

    @DeleteMapping("/{projectId}")
    public ResponseEntity<Map<String, String>> deleteProject(@PathVariable UUID projectId){
        Map<String, String> responseDto = projectService.deleteProject(projectId);
        return ResponseEntity.ok(responseDto);
    }
}
