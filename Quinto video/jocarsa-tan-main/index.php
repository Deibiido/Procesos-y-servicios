<!doctype html>
<html>
	<head>
		<script defer src="jocarsa_tan.js"></script>
		<style>
			table tbody tr td {
				text-align: center;
				padding: 10px;
			}
		</style>
	</head>
	<body>
		<?php
			$columnas = 8;
			$filas = 16;
		?>
		<h1>Una tabla</h1>
    <!-- Botón para randomizar valores -->
    <button id="randomizeButton">Randomize</button>
		<table class="jocarsa-tan" style="color:rgb(131, 23, 122);">
			<thead style="color:rgb(0,0,220)">
				<tr>
					<?php
						for($i = 0; $i < $columnas; $i++){
							echo '<th>'.$i.'</th>';
						}
					?>
				</tr>
			</thead>
			<tbody>
				<?php
					for($i = 0; $i < $filas; $i++){
						echo '<tr>';
						for($j = 0; $j < $columnas; $j++){
							echo '<td>'.rand(1,500).'</td>';
						}
						echo '</tr>';
					}
				?>
			</tbody>
		</table>
		<h1>Otra tabla</h1>
		<table>
			<thead>
				<tr>
					<?php
						for($i = 0; $i < $columnas; $i++){
							echo '<th>'.$i.'</th>';
						}
					?>
				</tr>
			</thead>
			<tbody>
				<?php
					for($i = 0; $i < $filas; $i++){
						echo '<tr>';
						for($j = 0; $j < $columnas; $j++){
							echo '<td>'.rand(1,500).'</td>';
						}
						echo '</tr>';
					}
				?>
			</tbody>
		</table>
	</body>
</html>
